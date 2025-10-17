try:
    from smbus2 import SMBus
except ImportError:
    class SMBus:
        def __init__(self, *a, **kw): pass
        def write_byte(self, *a, **kw): pass
        def read_byte(self, *a, **kw): return 128

class PCF8591:
    def __init__(self, bus=1, address=0x48, vref=3.3):
        self.bus = SMBus(bus)
        self.address = address
        self.vref = vref
        # try to load calibration file
        try:
            import yaml, os
            cfg_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'calibration.yaml')
            if os.path.exists(cfg_path):
                with open(cfg_path) as f:
                    self._cal = yaml.safe_load(f) or {}
            else:
                self._cal = {}
        except Exception:
            self._cal = {}

    def read_raw(self, ch: int) -> int:
        if not (0 <= ch <= 3):
            raise ValueError("Channel must be 0..3")
        control = 0x40 | ch
        self.bus.write_byte(self.address, control)
        _ = self.bus.read_byte(self.address)  # dummy read
        return self.bus.read_byte(self.address)

    def read_voltage(self, ch: int) -> float:
        v = round(self.read_raw(ch) / 255.0 * self.vref, 4)
        return v

    def read_calibrated(self, ch: int, sensor_name: str) -> float:
        """Read voltage on channel and apply linear calibration if available."""
        v = self.read_voltage(ch)
        cal = self._cal.get(sensor_name)
        if cal and isinstance(cal, dict) and 'a' in cal and 'b' in cal:
            return cal['a'] * v + cal['b']
        return v
