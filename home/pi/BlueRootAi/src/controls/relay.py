# from gpiozero import OutputDevice

# class Relay:
#     def __init__(self, pin: int, active_high: bool = False):
#         self.dev = OutputDevice(pin, active_high=active_high, initial_value=False)
#     def on(self): self.dev.on()
#     def off(self): self.dev.off()
#     @property
#     def is_on(self) -> bool: return bool(self.dev.value)
