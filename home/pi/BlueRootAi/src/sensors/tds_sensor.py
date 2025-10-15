"""
TDS Sensor reading via PCF8591 ADC (I2C)
AIN2 (Command 0x42)
"""
import smbus2
import time

class TDSSensor:
    def __init__(self, i2c_bus=1, address=0x48, channel=2):
        self.bus = smbus2.SMBus(i2c_bus)
        self.address = address
        self.channel = channel  # 2 for AIN2

    def read_raw(self):
        # PCF8591: control byte 0x40 | channel
        control_byte = 0x40 | self.channel
        self.bus.write_byte(self.address, control_byte)
        self.bus.read_byte(self.address)  # dummy read
        value = self.bus.read_byte(self.address)
        return value

    def read_tds(self):
        raw = self.read_raw()
        # Convert raw ADC value (0-255) to voltage (0-5V)
        voltage = raw * 5.0 / 255
        # Example conversion: TDS (ppm) = (voltage * 1000) / 2
        tds = (voltage * 1000) / 2
        return tds

if __name__ == "__main__":
    sensor = TDSSensor()
    while True:
        print(f"TDS: {sensor.read_tds():.2f} ppm")
        time.sleep(1)