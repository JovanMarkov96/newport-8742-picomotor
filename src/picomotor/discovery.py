# SPDX-License-Identifier: MIT
"""
Newport 8742 Picomotor Controller Discovery

Auto-detect connected Newport/New Focus 8742 controllers via USB.
"""

from typing import List, Dict, Optional, Any
import usb.core
import usb.util

# Newport/New Focus USB identifiers
# The 8742 controller uses these IDs (verify with your device)
NEWPORT_VENDOR_ID = 0x104D  # Newport Corporation
KNOWN_PRODUCT_IDS = [
    0x4000,  # 8742 Open-loop controller (common)
]


def discover_controllers(
    vendor_id: Optional[int] = None,
    product_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Discover all connected Newport 8742 Picomotor controllers.
    
    Args:
        vendor_id: Override vendor ID (default: Newport 0x104D)
        product_id: Override product ID (default: scan known IDs)
        
    Returns:
        List of dicts with device info:
        [
            {
                "vendor_id": 0x104D,
                "product_id": 0x4000,
                "bus": 1,
                "address": 5,
                "serial": "12345" or None,
                "manufacturer": "Newport" or None,
                "product": "8742" or None,
            },
            ...
        ]
    """
    vid = vendor_id or NEWPORT_VENDOR_ID
    pids = [product_id] if product_id else KNOWN_PRODUCT_IDS
    
    devices = []
    
    for pid in pids:
        try:
            found = usb.core.find(find_all=True, idVendor=vid, idProduct=pid)
            for dev in found:
                info = {
                    "vendor_id": dev.idVendor,
                    "product_id": dev.idProduct,
                    "bus": dev.bus,
                    "address": dev.address,
                    "serial": None,
                    "manufacturer": None,
                    "product": None,
                }
                
                # Try to get string descriptors (may fail without permissions)
                try:
                    if dev.iSerialNumber:
                        info["serial"] = usb.util.get_string(dev, dev.iSerialNumber)
                except (usb.core.USBError, ValueError):
                    pass
                    
                try:
                    if dev.iManufacturer:
                        info["manufacturer"] = usb.util.get_string(dev, dev.iManufacturer)
                except (usb.core.USBError, ValueError):
                    pass
                    
                try:
                    if dev.iProduct:
                        info["product"] = usb.util.get_string(dev, dev.iProduct)
                except (usb.core.USBError, ValueError):
                    pass
                
                devices.append(info)
                
        except usb.core.NoBackendError:
            print("[Discovery] No USB backend found. Install libusb.")
            break
        except usb.core.USBError as e:
            print(f"[Discovery] USB error scanning for PID {pid:#06x}: {e}")
            continue
    
    return devices


def find_first_controller(
    vendor_id: Optional[int] = None,
    product_id: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Find the first available Newport 8742 controller.
    
    Returns:
        Device info dict, or None if no controller found.
    """
    devices = discover_controllers(vendor_id, product_id)
    return devices[0] if devices else None


def print_discovered_controllers() -> None:
    """Print all discovered controllers (useful for debugging)."""
    devices = discover_controllers()
    
    if not devices:
        print("No Newport 8742 controllers found.")
        print("\nTroubleshooting:")
        print("  1. Check USB connection")
        print("  2. Ensure controller is powered on")
        print("  3. Install libusb drivers (Windows: use Zadig)")
        print(f"  4. Looking for Vendor ID: {NEWPORT_VENDOR_ID:#06x}")
        return
    
    print(f"Found {len(devices)} controller(s):\n")
    for i, dev in enumerate(devices, 1):
        print(f"  [{i}] VID={dev['vendor_id']:#06x} PID={dev['product_id']:#06x}")
        print(f"      Bus {dev['bus']}, Address {dev['address']}")
        if dev['manufacturer']:
            print(f"      Manufacturer: {dev['manufacturer']}")
        if dev['product']:
            print(f"      Product: {dev['product']}")
        if dev['serial']:
            print(f"      Serial: {dev['serial']}")
        print()


if __name__ == "__main__":
    print("Scanning for Newport 8742 Picomotor controllers...\n")
    print_discovered_controllers()
