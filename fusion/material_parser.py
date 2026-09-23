"""Extract Fusion appearances and preserve their actual display color."""

import traceback

import adsk.core
import adsk.fusion

from .material import Color, Material

app = adsk.core.Application.get()


def _appearance_color(appearance):
    if appearance is None:
        return None
    try:
        for prop_name in ("opaque_albedo", "diffuse", "color"):
            try:
                prop = appearance.appearanceProperties.itemByName(prop_name)
            except Exception:
                prop = None
            if prop is None:
                continue
            value = getattr(prop, "value", None)
            if value is None:
                continue
            # Fusion colors are commonly adsk.core.Color with 0..255 channels.
            if all(hasattr(value, channel) for channel in ("red", "green", "blue")):
                return Color(value.red / 255.0, value.green / 255.0, value.blue / 255.0, 1.0)
    except Exception:
        pass
    return None


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
    def __init__(self):
        self.design = app.activeProduct
        if not isinstance(self.design, adsk.fusion.Design):
            raise RuntimeError("No active Fusion Design.")
        self.root = self.design.rootComponent

    def update(self, robot):
        try:
            for occurrence in self.root.allOccurrences:
                component_name = occurrence.component.name
                link_name = "base_link" if component_name == "base_link" else _sanitize_name(occurrence.fullPathName)
                link = robot.get_link(link_name) or robot.get_link(component_name)
                if link is not None:
                    link.material = self._extract_material(occurrence)
        except Exception:
            print(traceback.format_exc())

    def _extract_material(self, occurrence):
        component = occurrence.component
        for body in component.bRepBodies:
            appearance = body.appearance
            if appearance:
                color = _appearance_color(appearance)
                return Material(name=appearance.name, color=color or Material().color)
        if component.appearance:
            color = _appearance_color(component.appearance)
            return Material(name=component.appearance.name, color=color or Material().color)
        return Material()

    def parse(self):
        materials = {}
        for occurrence in self.root.allOccurrences:
            try:
                materials[occurrence.component.name] = self._extract_material(occurrence)
            except Exception:
                print(traceback.format_exc())
        return materials
