"""
pH Sensor reading via PCF8591 ADC (I2C)
AIN0 (Command 0x40)
"""
import smbus
import time

ADDRESS = 0x48  # PCF8591 I2C address
bus = smbus.SMBus(1)

def read_ph():
    bus.write_byte(ADDRESS, 0x40)  # AIN0
    bus.read_byte(ADDRESS)  # dummy read
    raw = bus.read_byte(ADDRESS)
    voltage = (raw / 255.0) * 3.3
    ph = (voltage / 3.0) * 14  # rough, calibrate later
    return raw, voltage, ph

if __name__ == "__main__":
    print("🧪 pH Sensor Reading...")
    try:
        while True:
            raw, voltage, ph = read_ph()
            print(f"Raw: {raw:3d} | Voltage: {voltage:.2f} V | pH ~ {ph:.2f}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped")