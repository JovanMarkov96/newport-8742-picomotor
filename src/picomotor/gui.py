# SPDX-License-Identifier: MIT
"""
Newport 8742 Picomotor Controller GUI — Standalone Version

This GUI connects directly to the controller via USB.
It auto-discovers connected controllers and works without any server.

Usage:
    python -m picomotor.gui                    # Auto-discover and connect
    python -m picomotor.gui --config cfg.json  # Use custom channel labels
    python -m picomotor.gui --list             # List discovered controllers
"""

import sys
import json
import argparse
from typing import Dict, Any, Optional

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton,
    QLineEdit, QGroupBox, QHBoxLayout
)
from PyQt5.QtCore import QTimer

from .controller import HighLevelController
from .discovery import discover_controllers, NEWPORT_VENDOR_ID


class PicomotorGUI(QWidget):
    """
    Standalone GUI for Newport 8742 Picomotor Controller.
    
    Connects directly to USB — no server required.
    """
    
    def __init__(
        self,
        controller: Optional[HighLevelController] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__()
        self.controller = controller
        self.config = config or {}
        
        self.setWindowTitle("Newport 8742 Picomotor Control")
        self.positions = {}
        self.step_inputs = {}
        self.abs_inputs = {}
        self.pos_labels = {}
        self.buttons = {}
        self.channel_labels = {}  # channel_id -> label string
        
        self._load_channel_labels()
        self._build_ui()
        
        # Start position polling
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_positions)
        self.timer.start(500)
        self.update_positions()

    def _load_channel_labels(self):
        """Load channel labels from config or use defaults."""
        channels_cfg = self.config.get("channels", {})
        
        for ch in range(1, 5):
            ch_str = str(ch)
            if ch_str in channels_cfg:
                # Config can be string or dict
                cfg = channels_cfg[ch_str]
                if isinstance(cfg, str):
                    self.channel_labels[ch] = cfg
                elif isinstance(cfg, dict):
                    label = cfg.get("label") or cfg.get("role") or f"Motor {ch}"
                    self.channel_labels[ch] = label
                else:
                    self.channel_labels[ch] = f"Motor {ch}"
            else:
                self.channel_labels[ch] = f"Motor {ch}"

    def _build_ui(self):
        """Build the GUI layout."""
        main_layout = QVBoxLayout()
        
        # Header with connection status
        header = QHBoxLayout()
        header.addWidget(QLabel("Newport 8742 Picomotor Controller"))
        self.conn_label = QLabel("Disconnected" if not self.controller else "Connected")
        self.conn_label.setStyleSheet(
            "color: red;" if not self.controller else "color: green;"
        )
        header.addStretch()
        header.addWidget(self.conn_label)
        main_layout.addLayout(header)
        
        # Create UI for each motor channel (1-4)
        for channel in range(1, 5):
            label = self.channel_labels.get(channel, f"Motor {channel}")
            group = QGroupBox(f"{label} (Ch {channel})")
            vbox = QVBoxLayout()

            # Position row
            pos_row = QHBoxLayout()
            pos_row.addWidget(QLabel("Position:"))
            self.pos_labels[channel] = QLabel("---")
            pos_row.addWidget(self.pos_labels[channel])
            pos_row.addStretch()
            vbox.addLayout(pos_row)

            # Jog controls
            jog_row = QHBoxLayout()
            jog_row.addWidget(QLabel("Step:"))
            self.step_inputs[channel] = QLineEdit("100")
            self.step_inputs[channel].setFixedWidth(60)
            jog_row.addWidget(self.step_inputs[channel])
            
            btn_neg = QPushButton("◀ -")
            btn_pos = QPushButton("+ ▶")
            btn_neg.setFixedWidth(50)
            btn_pos.setFixedWidth(50)
            btn_neg.clicked.connect(lambda _, ch=channel: self.move_relative(ch, -1))
            btn_pos.clicked.connect(lambda _, ch=channel: self.move_relative(ch, 1))
            jog_row.addWidget(btn_neg)
            jog_row.addWidget(btn_pos)
            jog_row.addStretch()
            vbox.addLayout(jog_row)

            # Absolute controls
            abs_row = QHBoxLayout()
            abs_row.addWidget(QLabel("Target:"))
            self.abs_inputs[channel] = QLineEdit("0")
            self.abs_inputs[channel].setFixedWidth(60)
            abs_row.addWidget(self.abs_inputs[channel])
            
            btn_go = QPushButton("Go")
            btn_go.setFixedWidth(40)
            btn_go.clicked.connect(lambda _, ch=channel: self.move_absolute(ch))
            abs_row.addWidget(btn_go)
            
            btn_home = QPushButton("Set Zero")
            btn_home.clicked.connect(lambda _, ch=channel: self.set_home(ch))
            abs_row.addWidget(btn_home)
            abs_row.addStretch()
            vbox.addLayout(abs_row)

            group.setLayout(vbox)
            main_layout.addWidget(group)

            self.buttons[channel] = [btn_neg, btn_pos, btn_go, btn_home,
                                     self.step_inputs[channel], self.abs_inputs[channel]]
            self.positions[channel] = 0

        # Status bar
        self.status = QLabel("Ready.")
        main_layout.addWidget(self.status)
        
        self.setLayout(main_layout)

    def update_positions(self):
        """Poll current positions from controller."""
        if self.controller is None:
            return
            
        for channel in range(1, 5):
            try:
                motor_type = self.controller.get_motor_type(channel)
                if motor_type and ("Standard" in motor_type or "Tiny" in motor_type):
                    pos = self.controller.get_position(channel)
                    self.positions[channel] = pos
                    self.pos_labels[channel].setText(str(pos))
                    for w in self.buttons.get(channel, []):
                        w.setEnabled(True)
                else:
                    self.pos_labels[channel].setText("No motor")
                    for w in self.buttons.get(channel, []):
                        w.setEnabled(False)
            except Exception:
                self.pos_labels[channel].setText("Error")
                for w in self.buttons.get(channel, []):
                    w.setEnabled(False)

    def move_relative(self, channel: int, direction: int):
        """Move motor relative to current position."""
        if self.controller is None:
            self.status.setText("Not connected")
            return
        try:
            steps = int(self.step_inputs[channel].text()) * direction
            self.controller.move_relative(channel, steps)
            self.status.setText(f"Moved Ch{channel} by {steps} steps")
            self.update_positions()
        except Exception as e:
            self.status.setText(f"Move error: {e}")

    def move_absolute(self, channel: int):
        """Move motor to absolute position."""
        if self.controller is None:
            self.status.setText("Not connected")
            return
        try:
            target = int(self.abs_inputs[channel].text())
            self.controller.move_to_target(channel, target)
            self.status.setText(f"Moved Ch{channel} to {target}")
            self.update_positions()
        except Exception as e:
            self.status.setText(f"Move error: {e}")

    def set_home(self, channel: int):
        """Set current position as home (zero)."""
        if self.controller is None:
            self.status.setText("Not connected")
            return
        try:
            self.controller.set_home_position(channel)
            self.status.setText(f"Set Ch{channel} home")
            self.update_positions()
        except Exception as e:
            self.status.setText(f"Set home error: {e}")

    def closeEvent(self, event):
        """Clean up on window close."""
        self.timer.stop()
        event.accept()


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load config '{config_path}': {e}")
        return {}


def connect_controller(config: Dict[str, Any]) -> Optional[HighLevelController]:
    """
    Connect to controller, using config or auto-discovery.
    
    Config can specify:
        product_id: hex string or int
        vendor_id: hex string or int
    """
    def parse_id(val, default):
        if val is None:
            return default
        if isinstance(val, int):
            return val
        if isinstance(val, str):
            return int(val, 16) if val.startswith("0x") else int(val)
        return default
    
    vendor_id = parse_id(config.get("vendor_id"), NEWPORT_VENDOR_ID)
    product_id = parse_id(config.get("product_id"), None)
    
    # Auto-discover if no product_id specified
    if product_id is None:
        devices = discover_controllers(vendor_id=vendor_id)
        if not devices:
            return None
        product_id = devices[0]["product_id"]
        print(f"Auto-discovered controller: VID={vendor_id:#06x} PID={product_id:#06x}")
    
    try:
        velocity = config.get("velocity", 1000)
        acceleration = config.get("acceleration", 1000)
        
        controller = HighLevelController(
            product_id=product_id,
            vendor_id=vendor_id,
            velocity=velocity,
            acceleration=acceleration
        )
        return controller
    except Exception as e:
        print(f"Connection failed: {e}")
        return None


def main():
    """Main entry point for standalone GUI."""
    parser = argparse.ArgumentParser(
        description="Newport 8742 Picomotor Controller GUI"
    )
    parser.add_argument(
        "--config", "-c",
        help="Path to JSON config file for channel labels and connection settings"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List discovered controllers and exit"
    )
    parser.add_argument(
        "--vendor-id",
        help="Override vendor ID (hex, e.g., 0x104D)"
    )
    parser.add_argument(
        "--product-id",
        help="Override product ID (hex, e.g., 0x4000)"
    )
    
    args = parser.parse_args()
    
    # List mode
    if args.list:
        from .discovery import print_discovered_controllers
        print_discovered_controllers()
        return 0
    
    # Load config
    config = load_config(args.config) if args.config else {}
    
    # Override with command-line args
    if args.vendor_id:
        config["vendor_id"] = args.vendor_id
    if args.product_id:
        config["product_id"] = args.product_id
    
    # Connect to controller
    print("Connecting to Newport 8742 controller...")
    controller = connect_controller(config)
    
    if controller is None:
        print("\nNo controller found. Run with --list to see available devices.")
        print("Starting GUI in disconnected mode...")
    
    # Launch GUI
    app = QApplication(sys.argv)
    gui = PicomotorGUI(controller=controller, config=config)
    gui.show()
    
    result = app.exec_()
    
    # Cleanup
    if controller:
        try:
            controller.stop_motion()
        except:
            pass
    
    return result


if __name__ == "__main__":
    sys.exit(main())
