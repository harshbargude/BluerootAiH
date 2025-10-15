"""Calibration helpers for sensors.

Provides a simple linear calibrator (y = a*x + b) and load/save to YAML.
"""
from typing import Sequence, Tuple
import yaml
import os


class LinearCalibrator:
    def __init__(self, a: float = 1.0, b: float = 0.0):
        self.a = a
        self.b = b

    def calibrate_from_pairs(self, measured: Sequence[float], reference: Sequence[float]) -> Tuple[float, float]:
        """Fit a and b using least-squares for reference = a*measured + b."""
        if len(measured) != len(reference):
            raise ValueError("measured and reference must have same length")
        n = len(measured)
        if n == 0:
            raise ValueError("need at least one point")
        # simple linear regression
        xm = sum(measured) / n
        yr = sum(reference) / n
        num = sum((m - xm) * (r - yr) for m, r in zip(measured, reference))
        den = sum((m - xm) ** 2 for m in measured)
        if den == 0:
            # all measured equal -> vertical fit impossible; use offset-only
            a = 0.0
            b = yr
        else:
            a = num / den
            b = yr - a * xm
        self.a = a
        self.b = b
        return a, b

    def apply(self, measured: float) -> float:
        return self.a * measured + self.b

    def to_dict(self):
        return {"a": float(self.a), "b": float(self.b)}

    @classmethod
    def from_dict(cls, d):
        return cls(a=d.get("a", 1.0), b=d.get("b", 0.0))


def save_calibration(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        yaml.safe_dump(data, f)


def load_calibration(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}
