#!/usr/bin/env python
# SPDX-License-Identifier: MIT
"""
Basic example: Connect to controller and move motors.
"""

import sys
import os

# Add src to path for development (before package install)
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(root, 'src')
if src not in sys.path:
    sys.path.insert(0, src)

from picomotor import HighLevelController


def main():
    """Demonstrate basic motor control."""
    
    # TODO: Replace with your actual USB IDs
    # You can find these in Device Manager or using `lsusb` on Linux
    VENDOR_ID = 0x104D   # Newport
    PRODUCT_ID = 0x4000  # 8742 (check your device)
    
    print("Connecting to Newport 8742 controller...")
    
    try:
        controller = HighLevelController(
            product_id=PRODUCT_ID,
            vendor_id=VENDOR_ID,
            velocity=1000,
            acceleration=1000
        )
    except ValueError as e:
        print(f"Connection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check USB connection")
        print("  2. Verify vendor/product IDs match your device")
        print("  3. Install libusb drivers (Windows: use Zadig)")
        return 1
    
    # Example operations
    motor_id = 1
    
    # Get current position
    pos = controller.get_position(motor_id)
    print(f"\nMotor {motor_id} current position: {pos}")
    
    # Move relative
    steps = 100
    print(f"Moving motor {motor_id} by {steps} steps...")
    controller.move_relative(motor_id, steps)
    
    # Verify new position
    new_pos = controller.get_position(motor_id)
    print(f"Motor {motor_id} new position: {new_pos}")
    
    # Move back
    print(f"Moving back...")
    controller.move_relative(motor_id, -steps)
    
    final_pos = controller.get_position(motor_id)
    print(f"Motor {motor_id} final position: {final_pos}")
    
    print("\nDone!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
