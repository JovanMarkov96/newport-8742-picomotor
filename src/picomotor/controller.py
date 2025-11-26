# SPDX-License-Identifier: MIT
"""
Newport 8742 Picomotor Controller

Low-level and high-level interfaces for controlling Newport/New Focus
8742 series 4-axis open-loop picomotor controllers via USB.
"""

import re
import time
from typing import Optional, Tuple, List

import usb.core
import usb.util
import cmd

NEWFOCUS_COMMAND_REGEX = re.compile("([0-9]{0,1})([a-zA-Z?]{2,})([0-9+-]*)")
MOTOR_TYPE = {
    "0": "No motor connected",
    "1": "Motor Unknown",
    "2": "'Tiny' Motor",
    "3": "'Standard' Motor"
}
SYNC_COMMANDS = ['DH', 'MC', 'MV', 'PA', 'PR', 'XX']

# Default timeout for wait operations (seconds)
DEFAULT_WAIT_TIMEOUT = 60.0


class ControllerError(Exception):
    """Base exception for controller errors."""
    pass


class ConnectionError(ControllerError):
    """Raised when connection to controller fails."""
    pass


class TimeoutError(ControllerError):
    """Raised when a motion operation times out."""
    pass


class Controller:
    def __init__(self, product_id, vendor_id):
        self.product_id = product_id
        self.vendor_id = vendor_id
        self._connect()

    def _connect(self):
        """
        Connect to the controller via USB
        """
        # find the device
        self.dev = usb.core.find(
            idProduct=self.product_id,
            idVendor=self.vendor_id
        )
        if self.dev is None:
            raise ValueError('Device not found')

        # set the active configuration. With no arguments, the first
        # configuration will be the active one
        self.dev.set_configuration()
        # get an endpoint instance
        cfg = self.dev.get_active_configuration()
        intf = cfg[(0, 0)]

        self.ep_out = usb.util.find_descriptor(
            intf,
            # match the first OUT endpoint
            custom_match=lambda e: \
            usb.util.endpoint_direction(e.bEndpointAddress) == \
            usb.util.ENDPOINT_OUT)
        self.ep_in = usb.util.find_descriptor(
            intf,
            # match the first IN endpoint
            custom_match=lambda e: \
            usb.util.endpoint_direction(e.bEndpointAddress) == \
            usb.util.ENDPOINT_IN)

        assert (self.ep_out and self.ep_in) is not None



    def send_command(self, usb_command):
        """Send command to USB device endpoint

        Args:
            usb_command (str): Correctly formated command for USB driver
            get_reply (bool): query the IN endpoint after sending command, to
                get controller's reply

        Returns:
            Character representation of returned hex values if a reply is
                requested
        """
        self.ep_out.write(usb_command)
        if '?' in usb_command:
            return self.ep_in.read(100)

    def parse_command(self, newfocus_command):
        """
        Convert a NewFocus style command into a USB command

        Args:
            newfocus_command (str): of the form xxAAnn
                The general format of a command is a two character mnemonic (AA).
                Both upper and lower case are accepted. Depending on the command,
                it could also have optional or required preceding (xx) and/or
                following (nn) parameters.
        """
        match = NEWFOCUS_COMMAND_REGEX.match(newfocus_command)

        # Check to see if a regex match was found in the user submitted command
        if match:
            # Extract matched components of the command
            driver_number, command, parameter = match.groups()
            usb_command = f'{driver_number or ""} {command} {parameter or ""}\r'

            return usb_command.upper(), (driver_number, command.upper(), parameter)
        else:
            print(f'ERROR! Command {newfocus_command} was not a valid format')

    def parse_reply(self, reply):
        """
        Args:
            reply (list): list of bytes returns from controller in hex format

        Returns:
            reply (str): Cleaned string of controller reply
        """
        reply = ''.join([chr(x) for x in reply])
        return reply.rstrip()

    def command(self, command):
        """Send NewFocus formated command

        Args:
            command (str): Legal command listed in usermanual [2 - 6.2]

        Returns:
            reply (str): Human readable reply from controller
        """
        usb_command, _ = self.parse_command(command)

        reply = self.send_command(usb_command)

        if reply:
            return self.parse_reply(reply)


class HighLevelController(Controller):
    """High-level controller with blocking moves and convenience methods.
    
    Args:
        product_id: USB product ID of the controller
        vendor_id: USB vendor ID of the controller  
        velocity: Default velocity for all motors (steps/sec)
        acceleration: Default acceleration for all motors (steps/sec²)
        wait_timeout: Timeout for motion completion (seconds)
    """
    
    def __init__(self, product_id: int, vendor_id: int, velocity: int = 1000, 
                 acceleration: int = 1000, wait_timeout: float = DEFAULT_WAIT_TIMEOUT):
        super().__init__(product_id=product_id, vendor_id=vendor_id)
        self.wait_timeout = wait_timeout
        self.confirm_connection()
        # Initialize velocity/acceleration for all 4 motor channels
        for motor_idx in range(1, 5):
            self.set_velocity(motor_idx, velocity)
            self.set_acceleration(motor_idx, acceleration)

    def confirm_connection(self):
        # Confirm connection to user
        res = self.get_controller_details()
        print("Connected to Motor Controller Model {}. Firmware {} {} {}\n".format(
            *res.split(' ')
        ))
        for m in range(1, 5):
            res = self.get_motor_type(m)
            print(f"Motor #{m}: {res}")

    def command(self, command):
        """
        Make the command function synchronous by waiting for the motors to stop
        """
        usb_command, commannd_tuple = self.parse_command(command)

        motor_id, command, parameter = commannd_tuple
        if command in SYNC_COMMANDS:
            self.wait()
        reply = self.send_command(usb_command)

        if reply:
            return self.parse_reply(reply)

    def wait(self, timeout: Optional[float] = None) -> bool:
        """Wait for all motors to stop moving.
        
        Args:
            timeout: Maximum time to wait (seconds). Uses self.wait_timeout if None.
            
        Returns:
            True if all motors stopped, False if timeout occurred.
            
        Raises:
            TimeoutError: If timeout is reached and motors still moving.
        """
        timeout = timeout if timeout is not None else self.wait_timeout
        start_time = time.time()
        
        while True:
            # Check all 4 motor channels
            all_done = all(self.get_motion_done(m) for m in range(1, 5))
            if all_done:
                return True
                
            # Check timeout
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Motion did not complete within {timeout}s")
                
            time.sleep(0.1)

    def get_controller_details(self):
        return self.command('VE?')

    def set_acceleration(self, motor_id, acceleration):
        self.command(f'{motor_id}AC{acceleration}')

    def get_acceleration(self, motor_id):
        return int(self.command(f'{motor_id}AC?'))

    def set_home_position(self, motor_id):
        self.command(f'{motor_id}DH')

    def get_home_position(self, motor_id):
        return int(self.command(f'{motor_id}DH?'))

    def get_motion_done(self, motor_id):
        return bool(int(self.command(f'{motor_id}MD?')))

    def move_indefinitely(self, motor_id: int, direction: str) -> None:
        """Move motor indefinitely in given direction until stopped.
        
        Args:
            motor_id: Motor channel (1-4)
            direction: '+' for positive, '-' for negative
        """
        self.command(f'{motor_id}MV{direction}')
        time.sleep(0.5)
        self.wait()

    def get_motion_direction(self, motor_id):
        return int(self.command(f'{motor_id}MV?'))

    def move_to_target(self, motor_id, target):
        """
        Move to target position and wait for the motor to stop moving
        """
        target = int(target)
        self.command(f'{motor_id}PA{target}')

        position = self.get_position(motor_id)
        num_of_steps = abs(target - position)
        delay = num_of_steps / self.get_velocity(motor_id)
        time.sleep(delay)
        self.wait()

    def get_target(self, motor_id):
        return int(self.command(f'{motor_id}PA?'))

    def move_relative(self, motor_id, steps):
        """
        Move relative to current position and wait for the motor to stop moving
        """
        steps = int(steps)
        self.command(f'{motor_id}PR{steps}')
        delay = abs(steps) / self.get_velocity(motor_id)
        time.sleep(delay)
        self.wait()

    def get_target_relative(self, motor_id):
        return int(self.command(f'{motor_id}PR?'))

    def get_motor_type(self, motor_id):
        n = self.command(f'{motor_id}QM?')
        return MOTOR_TYPE[n]

    def stop_motion(self, motor_id=None):
        if motor_id:
            self.command(f'{motor_id}ST')
        self.command(f'ST')

    def get_position(self, motor_id):
        return int(self.command(f'{motor_id}TP?'))

    def set_velocity(self, motor_id, velocity):
        self.command(f'{motor_id}VA{velocity}')

    def get_velocity(self, motor_id):
        return int(self.command(f'{motor_id}VA?'))


class ControllerConsole(cmd.Cmd):
    intro = '''
        Picomotor Command Line
        ---------------------------

        Enter a valid command, or 'quit' to exit the program.

        Common Commands:
            xMV[+-]: .....Indefinitely move motor 'x' in + or - direction
                 ST: .....Stop all motor movement
              xPRnn: .....Move motor 'x' 'nn' steps
        \n
        '''
    prompt = '>> '

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def default(self, line):
        res = self.controller.command(line)
        if res:
            print(res)

    def do_quit(self, arg):
        'Exit the program'
        self.controller.stop_motion()
        return True


def main():
    """Command-line interface entry point."""
    import argparse
    from .discovery import discover_controllers, find_first_controller, NEWPORT_VENDOR_ID

    parser = argparse.ArgumentParser(
        description="Newport 8742 Picomotor Controller CLI"
    )
    parser.add_argument(
        "--vendor-id",
        default="0x104D",
        help="Vendor ID in hex (default: 0x104D)"
    )
    parser.add_argument(
        "--product-id",
        help="Product ID in hex (default: auto-discover)"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List discovered controllers and exit"
    )
    
    args = parser.parse_args()
    
    # Parse IDs
    vendor_id = int(args.vendor_id, 16) if args.vendor_id.startswith("0x") else int(args.vendor_id)
    
    if args.list:
        from .discovery import print_discovered_controllers
        print_discovered_controllers()
        return
    
    # Find product ID if not specified
    if args.product_id:
        product_id = int(args.product_id, 16) if args.product_id.startswith("0x") else int(args.product_id)
    else:
        device = find_first_controller(vendor_id=vendor_id)
        if device is None:
            print("No Newport 8742 controller found. Use --list to see available devices.")
            return
        product_id = device["product_id"]
        print(f"Auto-discovered: VID={vendor_id:#06x} PID={product_id:#06x}")
    
    # Connect and start console
    try:
        controller = HighLevelController(
            product_id=product_id,
            vendor_id=vendor_id
        )
        console = ControllerConsole(controller)
        console.cmdloop()
    except Exception as e:
        print(f"Failed to connect: {e}")


if __name__ == '__main__':
    main()