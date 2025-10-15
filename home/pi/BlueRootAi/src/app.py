import os
import threading
import time
import yaml
from flask import Flask, jsonify, render_template, request
from sensors.utils import PCF8591
from controls.relay import Relay

# Temperature sensor import (DS18B20). Use a safe fallback on non-Pi systems.
try:
    from sensors.temperature_sensor import DS18B20
except Exception:
    class DS18B20:  # mock
        def __init__(self):
            pass
        def read_temperature(self):
            return None
# If using wrappers:
# from controls.pump_control import Pump
# from controls.valve_control import Valve

sensor_state = {"ph": None, "tds": None, "turb": None, "temp": None, "error": None}
_started = False

def load_config():
    cfg_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
    with open(cfg_path) as f:
        return yaml.safe_load(f)

def create_app():
    global _started
    app = Flask(__name__, static_folder="../static", template_folder="../templates")
    cfg = load_config()

    # Hardware
    adc = PCF8591(
        bus=cfg["adc"]["bus"],
        address=cfg["adc"]["address"],
        vref=cfg["adc"]["vref"]
    )
    ch = cfg["adc"]["channels"]

    # Temperature sensor (if present)
    try:
        temp_sensor = DS18B20()
    except Exception:
        temp_sensor = None

    pump = Relay(cfg["gpio"]["pump_pin"], active_high=cfg["gpio"]["relay_active_high"])
    valve = Relay(cfg["gpio"]["valve_pin"], active_high=cfg["gpio"]["relay_active_high"])
    # If using wrappers:
    # pump = Pump(cfg["gpio"]["pump_pin"], active_high=cfg["gpio"]["relay_active_high"])
    # valve = Valve(cfg["gpio"]["valve_pin"], active_high=cfg["gpio"]["relay_active_high"])

    def poll():
        while True:
            try:
                # read calibrated values if calibration exists (voltage -> unit)
                try:
                    ph_val = adc.read_calibrated(ch["ph"], 'ph')
                except Exception:
                    ph_val = adc.read_voltage(ch["ph"])  # fallback to voltage

                try:
                    tds_val = adc.read_calibrated(ch["tds"], 'tds')
                except Exception:
                    tds_val = adc.read_voltage(ch["tds"])  # fallback

                try:
                    turb_val = adc.read_calibrated(ch["turbidity"], 'turbidity')
                except Exception:
                    turb_val = adc.read_voltage(ch["turbidity"])  # fallback

                # temperature
                try:
                    temp_raw = temp_sensor.read_temperature() if temp_sensor else None
                    # apply temp calibration if present in adc._cal
                    temp_cal = getattr(adc, '_cal', {}) or {}
                    if temp_raw is not None and 'temp' in temp_cal:
                        a = temp_cal['temp'].get('a', 1.0)
                        b = temp_cal['temp'].get('b', 0.0)
                        temp_val = a * temp_raw + b
                    else:
                        temp_val = temp_raw
                except Exception:
                    temp_val = None

                sensor_state["ph"] = None if ph_val is None else round(float(ph_val), 3)
                sensor_state["tds"] = None if tds_val is None else round(float(tds_val), 2)
                sensor_state["turb"] = None if turb_val is None else round(float(turb_val), 2)
                sensor_state["temp"] = None if temp_val is None else round(float(temp_val), 2)
                sensor_state["error"] = None
            except Exception as e:
                sensor_state["error"] = str(e)
            time.sleep(2)

    if not _started:
        threading.Thread(target=poll, daemon=True).start()
        _started = True

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.get("/api/sensors")
    def get_sensors():
        return jsonify(sensor_state)

    @app.get("/api/control/state")
    def get_state():
        return jsonify({"pump": pump.is_on, "valve": valve.is_on})

    @app.post("/api/control/pump")
    def set_pump():
        on = bool(request.json.get("on"))
        pump.on() if on else pump.off()
        return jsonify({"pump": pump.is_on})

    @app.post("/api/control/valve")
    def set_valve():
        on = bool(request.json.get("on"))
        # If using wrapper: valve.open() if on else valve.close()
        valve.on() if on else valve.off()
        return jsonify({"valve": valve.is_on})

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000)
