# sensors/temperature_sensor.py

"""
DS18B20 Temperature Sensor (1-Wire, GPIO 4)
"""
import os
import glob
import time

class DS18B20:
    def __init__(self):
        # 1-Wire devices are in /sys/bus/w1/devices/
        # Enable 1-Wire in `sudo raspi-config` -> Interface Options
        base_dir = '/sys/bus/w1/devices/'
        device_folders = glob.glob(base_dir + '28-*')
        
        if not device_folders:
            # This error will be caught by the main app.py, allowing it to run without a sensor.
            raise RuntimeError('DS18B20 sensor not found. Check wiring and 1-Wire configuration.')
        
        # NOTE: This will only use the first sensor found.
        self.device_file = device_folders[0] + '/w1_slave'

    def read_temp_raw(self):
        """Reads the raw sensor data from the file."""
        try:
            with open(self.device_file, 'r') as f:
                lines = f.readlines()
            return lines
        except IOError:
            # Return empty list on file read error
            return []

    def read_temperature(self):
        """Reads and parses the temperature, returns it in Celsius."""
        lines = self.read_temp_raw()
        
        # IMPROVED: Add retries and checks for file format to prevent crashes.
        # Retry up to 5 times if the reading is not valid (CRC check failed).
        retries = 5
        while (len(lines) < 2 or lines[0].strip()[-3:] != 'YES') and retries > 0:
            time.sleep(0.2)
            lines = self.read_temp_raw()
            retries -= 1

        # If still no valid reading after retries, return None
        if len(lines) < 2 or lines[0].strip()[-3:] != 'YES':
            return None

        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            try:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                return temp_c
            except (ValueError, IndexError):
                # Return None if parsing fails
                return None
        
        return None

# The test script remains a great way to debug the sensor independently
if __name__ == "__main__":
    try:
        sensor = DS18B20()
        while True:
            temp = sensor.read_temperature()
            if temp is not None:
                print(f"Temperature: {temp:.2f} °C")
            else:
                print("Failed to read temperature.")
            time.sleep(1)
    except RuntimeError as e:
        print(e)
    except KeyboardInterrupt:
        print("\nExiting.")
