"""Interactive calibration helper.

Usage: python src/sensors/calibrate_sensor.py --sensor ph
It will prompt for reference values and measured voltages/readings.

Saves results to config/calibration.yaml under the sensor key.
"""
import argparse
import json
import sys
from sensors.calibration import LinearCalibrator, load_calibration, save_calibration
import os


def prompt_pairs():
    print("Enter calibration pairs. One per line as: <measured> <reference>")
    print("Empty line when done.")
    measured = []
    reference = []
    while True:
        try:
            line = input('> ').strip()
        except EOFError:
            break
        if not line:
            break
        parts = line.split()
        if len(parts) < 2:
            print("need two numbers")
            continue
        m = float(parts[0])
        r = float(parts[1])
        measured.append(m)
        reference.append(r)
    return measured, reference


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--sensor', required=True, choices=['ph', 'tds', 'turbidity', 'temp'])
    p.add_argument('--out', default=os.path.join('..', 'config', 'calibration.yaml'))
    args = p.parse_args()

    print(f"Calibrating {args.sensor}. Enter measured (voltage) then reference (true units)")
    measured, reference = prompt_pairs()
    if not measured:
        print("no points entered, abort")
        sys.exit(1)
    c = LinearCalibrator()
    a, b = c.calibrate_from_pairs(measured, reference)
    print(f"Fitted: value = {a:.6f} * measured + {b:.6f}")

    outpath = os.path.abspath(os.path.join(os.path.dirname(__file__), args.out))
    data = load_calibration(outpath)
    data[args.sensor] = c.to_dict()
    save_calibration(outpath, data)
    print("Saved to", outpath)


if __name__ == '__main__':
    main()
