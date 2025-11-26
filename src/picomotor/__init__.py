# SPDX-License-Identifier: MIT
"""
Newport 8742 Picomotor Controller Package

Python control interface for Newport/New Focus 8742 series
4-axis open-loop picomotor controllers.
"""

from .controller import (
    Controller,
    HighLevelController,
    ControllerConsole,
    ControllerError,
    ConnectionError,
    TimeoutError,
)
from .discovery import (
    discover_controllers,
    find_first_controller,
    print_discovered_controllers,
    NEWPORT_VENDOR_ID,
    KNOWN_PRODUCT_IDS,
)

__all__ = [
    # Controller classes
    "Controller",
    "HighLevelController", 
    "ControllerConsole",
    # Exceptions
    "ControllerError",
    "ConnectionError",
    "TimeoutError",
    # Discovery
    "discover_controllers",
    "find_first_controller",
    "print_discovered_controllers",
    "NEWPORT_VENDOR_ID",
    "KNOWN_PRODUCT_IDS",
]
__version__ = "0.1.0"
