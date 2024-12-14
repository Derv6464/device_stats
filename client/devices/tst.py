import asyncio
from bleak import BleakScanner, BleakClient

# BLE Service and Characteristic UUIDs
SERVICE_UUID = "00000180-0000-1000-8000-00805f9b34fb"  # 0x180 in UUID format
READ_CHAR_UUID = "0000fef4-0000-1000-8000-00805f9b34fb"  # 0xFEF4 in UUID format
WRITE_CHAR_UUID = "0000dead-0000-1000-8000-00805f9b34fb"  # 0xDEAD in UUID format
TARGET_DEVICE_NAME = "Dervla BLE"

async def main():
    print("Scanning for BLE devices...")
    
    # Scan for devices
    devices = await BleakScanner.discover()
    
    # Find the target device by name
    target_device = None
    for device in devices:
        print(f"Found device: {device.name} ({device.address})")
        if device.name == TARGET_DEVICE_NAME:
            target_device = device
            break
    
    if not target_device:
        print(f"Device with name '{TARGET_DEVICE_NAME}' not found.")
        return
    
    print(f"Found target device: {target_device.name} ({target_device.address})")
    
    # Connect to the target device
    async with BleakClient(target_device.address) as client:
        print(f"Connected to {target_device.name}")
        print(f"Is connected: {await client.is_connected()}")
        
        # Read from the characteristic
        try:
            read_value = await client.read_gatt_char(READ_CHAR_UUID)
            print(f"Read from characteristic {READ_CHAR_UUID}: {read_value}")
        except Exception as e:
            print(f"Failed to read characteristic: {e}")
        
        # Write to the characteristic
        try:
            write_value = b"Hello, BLE!"  # Example value to write
            await client.write_gatt_char(WRITE_CHAR_UUID, write_value)
            print(f"Wrote to characteristic {WRITE_CHAR_UUID}: {write_value}")
        except Exception as e:
            print(f"Failed to write to characteristic: {e}")

# Run the asyncio even
asyncio.run(main())