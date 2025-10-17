"""
Turbidity Sensor reading via PCF8591 ADC (I2C)
AIN1 (Command 0x41)
"""
import smbus2
import time

class TurbiditySensor:
    def __init__(self, i2c_bus=1, address=0x48, channel=1):
        self.bus = smbus2.SMBus(i2c_bus)
        self.address = address
        self.channel = channel  # 1 for AIN1

    def read_raw(self):
        control_byte = 0x40 | self.channel
        self.bus.write_byte(self.address, control_byte)
        self.bus.read_byte(self.address)  # dummy read
        value = self.bus.read_byte(self.address)
        return value

    def read_turbidity(self):
        raw = self.read_raw()
        # Convert raw ADC value (0-255) to voltage (0-5V)
        voltage = raw * 5.0 / 255
        # Example: higher voltage = lower turbidity (clearer water)
        return voltage

if __name__ == "__main__":
    sensor = TurbiditySensor()
    while True:
        print(f"Turbidity voltage: {sensor.read_turbidity():.2f} V")
        time.sleep(1)