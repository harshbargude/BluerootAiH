from .relay import Relay
class Valve:
    def __init__(self, pin: int, active_high: bool=False):
        self.r = Relay(pin, active_high)
    def open(self): self.r.on()
    def close(self): self.r.off()
    @property
    def is_open(self): return self.r.is_on
