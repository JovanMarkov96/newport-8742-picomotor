# Examples

Example scripts demonstrating Newport 8742 Picomotor controller usage.

## Available Examples

| Script | Description |
|--------|-------------|
| `basic_control.py` | Connect and perform basic motor moves |

## Running Examples

Before running, ensure you have the package installed:

```bash
cd ..
pip install -e .
```

Then run any example:

```bash
python basic_control.py
```

## Notes

- Update `VENDOR_ID` and `PRODUCT_ID` in each script to match your hardware
- Windows users may need libusb drivers installed via Zadig
