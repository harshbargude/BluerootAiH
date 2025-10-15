"""
DS18B20 Temperature Sensor (1-Wire, GPIO 4)
"""
import os
import glob
import time

class DS18B20:
    def __init__(self):
        # 1-Wire devices are in /sys/bus/w1/devices/28-*/
        base_dir = '/sys/bus/w1/devices/'
        device_folders = glob.glob(base_dir + '28-*')
        if not device_folders:
            raise RuntimeError('No DS18B20 sensor found!')
        self.device_file = device_folders[0] + '/w1_slave'

    def read_temp_raw(self):
        with open(self.device_file, 'r') as f:
            lines = f.readlines()
        return lines

    def read_temperature(self):
        lines = self.read_temp_raw()
        # Wait for a valid reading
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
        return None

if __name__ == "__main__":
    sensor = DS18B20()
    while True:
        print(f"Temperature: {sensor.read_temperature():.2f} °C")
        time.sleep(1)