from .relay import Relay
class Pump:
    def __init__(self, pin: int, active_high: bool=False):
        self.r = Relay(pin, active_high)
    def on(self): self.r.on()
    def off(self): self.r.off()
    @property
    def is_on(self): return self.r.is_on
