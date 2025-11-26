# Newport 8742 Picomotor Controller

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: PEP8](https://img.shields.io/badge/code%20style-PEP8-green.svg)](https://peps.python.org/pep-0008/)

Python library for controlling Newport/New Focus 8742 series 4-axis open-loop picomotor controllers via USB.

## Table of Contents

- [Features](#features)
- [Supported Hardware](#supported-hardware)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Auto-Discovery](#auto-discovery)
- [Standalone GUI](#standalone-gui)
- [Command-Line Interface](#command-line-interface)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [Safety Considerations](#safety-considerations)
- [Contributing](#contributing)
- [License](#license)

## Features

- **USB Communication** — Direct control via pyusb
- **Multi-Motor Support** — Control up to 4 motors per controller
- **Synchronous Operations** — Blocking moves with automatic wait
- **Command-Line Interface** — Interactive REPL for testing
- **GUI Interface** — PyQt5-based control panel (optional)

## Supported Hardware

| Model | Description | Motors |
|-------|-------------|--------|
| 8742 | Open-loop 4-axis picomotor controller | 4 |

Motor types detected automatically:
- Standard Motor
- Tiny Motor

## Installation

```bash
# From this directory
pip install -e .

# Or with GUI support
pip install -e ".[gui]"
```

### USB Driver Setup (Windows)

You may need to install libusb drivers:
1. Download [Zadig](https://zadig.akeo.ie/)
2. Connect the 8742 controller
3. In Zadig, select the device and install WinUSB driver

### USB Driver Setup (Linux)

Add a udev rule for non-root access:
```bash
# Create /etc/udev/rules.d/99-newport.rules
SUBSYSTEM=="usb", ATTR{idVendor}=="104d", ATTR{idProduct}=="4000", MODE="0666"

# Reload rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Quick Start

```python
from picomotor import HighLevelController

# Connect to controller (use your actual vendor/product IDs)
controller = HighLevelController(
    product_id=0x4000,  # Check your device
    vendor_id=0x104D    # Newport vendor ID
)

# Move motor 1 to position 1000
controller.move_to_target(motor_id=1, target=1000)

# Get current position
pos = controller.get_position(motor_id=1)
print(f"Motor 1 position: {pos}")

# Move relative
controller.move_relative(motor_id=1, steps=500)
```

## Auto-Discovery

Automatically find connected Newport 8742 controllers:

```python
from picomotor import discover_controllers, find_first_controller

# Find all connected controllers
controllers = discover_controllers()
for ctrl in controllers:
    print(f"Found: {ctrl['description']} at bus {ctrl['bus']}:{ctrl['address']}")

# Or just get the first one
first = find_first_controller()
if first:
    controller = HighLevelController(
        product_id=first['product_id'],
        vendor_id=first['vendor_id']
    )
```

## Standalone GUI

Launch the graphical interface:

```bash
# Auto-discover and connect
python -m picomotor.gui

# Or with custom channel labels via config file
python -m picomotor.gui --config motors.json
```

Example `motors.json` configuration:
```json
{
  "channels": {
    "1": "674 Vertical",
    "2": "674 Horizontal",
    "3": "1092 Vertical",
    "4": "1092 Horizontal"
  }
}
```

## Command-Line Interface

```bash
python -m picomotor.controller
```

```
Picomotor Command Line
---------------------------

Enter a valid command, or 'quit' to exit the program.

Common Commands:
    xMV[+-]: .....Indefinitely move motor 'x' in + or - direction
         ST: .....Stop all motor movement
      xPRnn: .....Move motor 'x' 'nn' steps

>> 1PR100    # Move motor 1 by 100 steps
>> 1TP?      # Query motor 1 position
>> ST        # Stop all motors
>> quit
```

## API Reference

### Controller Classes

| Class | Description |
|-------|-------------|
| `Controller` | Low-level USB communication |
| `HighLevelController` | High-level with blocking moves and convenience methods |
| `ControllerConsole` | Interactive command-line interface |

### HighLevelController Methods

| Method | Description |
|--------|-------------|
| `move_to_target(motor_id, target)` | Move to absolute position |
| `move_relative(motor_id, steps)` | Move relative to current position |
| `get_position(motor_id)` | Get current position |
| `set_home_position(motor_id)` | Set current position as home (0) |
| `get_motor_type(motor_id)` | Get connected motor type |
| `set_velocity(motor_id, velocity)` | Set motor velocity |
| `set_acceleration(motor_id, acceleration)` | Set motor acceleration |
| `stop_motion(motor_id=None)` | Stop motion (all or specific motor) |

## Project Structure

```
Newport_8742/
├── src/picomotor/
│   ├── __init__.py      # Package exports
│   ├── controller.py    # Controller classes
│   └── gui.py           # PyQt5 GUI
├── docs/manuals/        # PDF documentation
├── examples/            # Usage examples
├── pyproject.toml       # Package metadata
├── requirements.txt     # Dependencies
└── README.md
```

## Documentation

PDF manuals are available in `docs/manuals/`:
- `8742-Datasheet.pdf` — Specifications
- `8742-User-Manual.pdf` — Full command reference
- `8742-Series-Quick-Start-Guide.pdf` — Getting started

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| `usb.core.NoBackendError` | Install libusb: `pip install libusb` or install from [libusb.info](https://libusb.info/) |
| `usb.core.USBError: Access denied` | **Windows:** Run Zadig to install WinUSB driver. **Linux:** Add udev rule (see Installation) |
| Device not found | Check USB connection, verify device shows in Device Manager (Windows) or `lsusb` (Linux) |
| Wrong motor moves | Verify motor_id (1-4) corresponds to physical port label |
| Movement timeout | Motor may be at limit or disconnected; check `wait()` timeout parameter |
| Position drift | Picomotors are open-loop; use external feedback for precision applications |

### Debugging

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Verify USB connection:
```python
from picomotor import discover_controllers
controllers = discover_controllers()
print(f"Found {len(controllers)} controller(s)")
```

## Safety Considerations

> ⚠️ **WARNING:** Picomotors can damage sensitive optical equipment if misused.

### Before Operating

1. **Know your limits** — Document the safe travel range for each axis
2. **Start slow** — Use low velocity settings when testing new configurations
3. **Monitor visually** — Watch the first few movements of any new script
4. **Use soft limits** — Implement position bounds in your control software

### Best Practices

- **Never leave unattended** — Always supervise automated scanning operations
- **Implement emergency stop** — Ensure you can halt motion immediately (ST command)
- **Backup positions** — Record known-good positions before experiments
- **Check connections** — Loose motor cables can cause erratic behavior

### Position Reference

Picomotors are **open-loop** — they do not have built-in position feedback:
- Position values are step counts from the last zero reference
- Power cycling resets the position counter
- Physical position may drift over time due to mechanical slip

For precision applications, use external position sensors (e.g., encoders, cameras).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License — see [LICENSE](LICENSE) for details.
