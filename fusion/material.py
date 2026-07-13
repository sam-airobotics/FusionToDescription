"""
material.py

Material data models shared across the exporter.
"""

from dataclasses import dataclass, field


# ==========================================================
# Color
# ==========================================================

@dataclass
class Color:
    r: float = 0.7
    g: float = 0.7
    b: float = 0.7
    a: float = 1.0


# ==========================================================
# Material
# ==========================================================

@dataclass
class Material:

    name: str = "Default"

    color: Color = field(
        default_factory=Color
    )