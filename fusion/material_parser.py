"""
material_parser.py

Extracts material/appearance information from the Fusion 360 design.
"""

import traceback

import adsk.core
import adsk.fusion

from .material import Material

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


class MaterialParser:
    """Extract Fusion appearances without changing the established material behavior."""

    def __init__(self):
        self.design = app.activeProduct
        if not isinstance(self.design, adsk.fusion.Design):
            raise RuntimeError("No active Fusion Design.")
        self.root = self.design.rootComponent

    def update(self, robot):
        try:
            for occurrence in self.root.allOccurrences:
                component_name = occurrence.component.name
                link = robot.get_link(component_name)
                if link is None:
                    link = robot.get_link(
                        "base_link" if component_name == "base_link" else _sanitize_name(occurrence.fullPathName)
                    )
                if link is None:
                    continue
                link.material = self._extract_material(occurrence)
        except Exception:
            print(traceback.format_exc())

    def _extract_material(self, occurrence):
        component = occurrence.component
        for body in component.bRepBodies:
            if body.appearance:
                return Material(name=body.appearance.name)
        if component.appearance:
            return Material(name=component.appearance.name)
        return Material()

    def parse(self):
        materials = {}
        try:
            for occurrence in self.root.allOccurrences:
                materials[occurrence.component.name] = self._extract_material(occurrence)
        except Exception:
            print(traceback.format_exc())
        return materials
