# app.py

import os
import threading
import time
import yaml
from flask import Flask, jsonify, render_template, request
# ADDED: CORS is essential for your React frontend to communicate with this backend.
from flask_cors import CORS
from sensors.utils import PCF8591
from controls.relay import Relay

# Temperature sensor import (DS18B20). Use a safe fallback on non-Pi systems.
try:
    from sensors.temperature_sensor import DS18B20
except (ImportError, RuntimeError): # IMPROVED: Catch both import and runtime errors
    print("WARNING: Could not import or initialize DS18B20. Temperature readings will be disabled.")
    # This mock class ensures the rest of the app doesn't crash
    class DS18B20:
        def read_temperature(self):
            return None

# Global state dictionary for sensor readings
sensor_state = {"ph": None, "tds": None, "turb": None, "temp": None, "error": None}
# Flag to ensure the polling thread is started only once
_started = False

def load_config():
    # Assuming config.yaml is in a 'config' folder at the project root
    cfg_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
    with open(cfg_path) as f:
        return yaml.safe_load(f)

def create_app():
    global _started
    app = Flask(__name__, static_folder="../static", template_folder="../templates")
    # ADDED: Initialize CORS, allowing all origins for development.
    # For production, you might restrict this to your frontend's domain.
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    cfg = load_config()

    # Hardware Initialization
    adc = PCF8591(
        bus=cfg["adc"]["bus"],
        address=cfg["adc"]["address"],
        vref=cfg["adc"]["vref"]
    )
    ch = cfg["adc"]["channels"]

    # IMPROVED: More robust initialization for the temperature sensor
    temp_sensor = DS18B20()

    pump = Relay(cfg["gpio"]["pump_pin"], active_high=cfg["gpio"]["relay_active_high"])
    valve = Relay(cfg["gpio"]["valve_pin"], active_high=cfg["gpio"]["relay_active_high"])

    def poll():
        """Background thread to continuously poll sensors."""
        while True:
            try:
                # --- Read ADC sensors with fallback to raw voltage ---
                ph_val = adc.read_calibrated(ch["ph"], 'ph') if 'ph' in ch else None
                tds_val = adc.read_calibrated(ch["tds"], 'tds') if 'tds' in ch else None
                turb_val = adc.read_calibrated(ch["turbidity"], 'turbidity') if 'turbidity' in ch else None

                # --- Read Temperature Sensor ---
                temp_val = temp_sensor.read_temperature()

                # DESIGN NOTE: Applying a secondary calibration here is fine, but consider
                # moving this logic into the DS18B20 class itself for better encapsulation.
                temp_cal = cfg.get('calibration', {}).get('temp', {})
                if temp_val is not None and temp_cal:
                    a = temp_cal.get('a', 1.0)
                    b = temp_cal.get('b', 0.0)
                    temp_val = a * temp_val + b

                # --- Update global state safely ---
                sensor_state["ph"] = round(ph_val, 3) if ph_val is not None else None
                sensor_state["tds"] = round(tds_val, 2) if tds_val is not None else None
                sensor_state["turb"] = round(turb_val, 2) if turb_val is not None else None
                sensor_state["temp"] = round(temp_val, 2) if temp_val is not None else None
                sensor_state["error"] = None # Clear previous error on success
            except Exception as e:
                # If any sensor fails, log the error to the state
                print(f"Error in polling thread: {e}") # Log to console for debugging
                sensor_state["error"] = str(e)
            
            time.sleep(2) # Wait before next poll

    # Start the polling thread only once
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

    # CORRECTED: This endpoint is now safe from invalid requests.
    @app.post("/api/control/pump")
    def set_pump():
        data = request.get_json()
        if data is None or 'on' not in data:
            return jsonify({"error": "Invalid request. 'on' field is missing."}), 400
        
        on = bool(data.get("on"))
        pump.on() if on else pump.off()
        return jsonify({"pump": pump.is_on, "status": "success"})

    # CORRECTED: This endpoint is also safe now.
    @app.post("/api/control/valve")
    def set_valve():
        data = request.get_json()
        if data is None or 'on' not in data:
            return jsonify({"error": "Invalid request. 'on' field is missing."}), 400

        on = bool(data.get("on"))
        valve.on() if on else valve.off()
        return jsonify({"valve": valve.is_on, "status": "success"})

    return app

if __name__ == "__main__":
    app = create_app()
    # Use port 5000 as a common convention for Flask dev servers
    app.run(host="0.0.0.0", port=5000)
