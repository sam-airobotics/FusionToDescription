"""
transform_parser.py

Extracts occurrence transforms from the active Fusion 360 design.
"""

import traceback

import adsk.core
import adsk.fusion

app = adsk.core.Application.get()


def _sanitize_name(value):
    result = str(value or "")
    for char in ("/", "\\", " ", ":", "-", "."):
        result = result.replace(char, "_")
    while "__" in result:
        result = result.replace("__", "_")
    result = result.strip("_") or "unnamed"
    if not result[0].isalpha():
        result = f"link_{result}"
    return result


class TransformParser:
    """Extract transforms keyed by the same occurrence-based link names as joints."""

    def __init__(self):
        self.design = app.activeProduct
        if not isinstance(self.design, adsk.fusion.Design):
            raise RuntimeError("No active Fusion Design.")
        self.root = self.design.rootComponent

    def parse(self):
        transforms = {}
        try:
            for occurrence in self.root.allOccurrences:
                component_name = occurrence.component.name
                name = "base_link" if component_name == "base_link" else _sanitize_name(occurrence.fullPathName)
                transforms[name] = self._parse_transform(occurrence)
                transforms.setdefault(component_name, transforms[name])
        except Exception as exc:
            print(f"Error parsing transforms: {str(exc)}")
            print(traceback.format_exc())
        return transforms

    @staticmethod
    def _parse_transform(occurrence):
        matrix = occurrence.transform2
        translation = matrix.translation
        return {
            "translation": {
                "x": translation.x,
                "y": translation.y,
                "z": translation.z,
            },
            "rotation": {
                "r11": matrix.getCell(0, 0), "r12": matrix.getCell(0, 1), "r13": matrix.getCell(0, 2),
                "r21": matrix.getCell(1, 0), "r22": matrix.getCell(1, 1), "r23": matrix.getCell(1, 2),
                "r31": matrix.getCell(2, 0), "r32": matrix.getCell(2, 1), "r33": matrix.getCell(2, 2),
            },
        }
