"""
material_parser.py

Extracts material/appearance information from the
Fusion 360 design.

The extracted information is stored in the RobotModel
and later used by materials_xacro_generator.py.
"""

import traceback

import adsk.core
import adsk.fusion

from .robot_model import Material

app = adsk.core.Application.get()


class MaterialParser:

    def __init__(self):

        self.design = app.activeProduct

        if not isinstance(self.design, adsk.fusion.Design):
            raise RuntimeError("No active Fusion Design.")

        self.root = self.design.rootComponent

    # =====================================================
    # Update Robot Model
    # =====================================================

    def update(self, robot):

        try:

            for occurrence in self.root.occurrences:

                component_name = occurrence.component.name

                link = robot.get_link(component_name)

                if link is None:
                    continue

                link.material = self._extract_material(occurrence)

        except Exception:

            print(traceback.format_exc())

    # =====================================================
    # Extract Material
    # =====================================================

    def _extract_material(self, occurrence):

        component = occurrence.component

        # -------------------------------------------------
        # Check Body Appearance
        # -------------------------------------------------

        for body in component.bRepBodies:

            if body.appearance:

                return Material(
                    name=body.appearance.name
                )

        # -------------------------------------------------
        # Component Appearance
        # -------------------------------------------------

        if component.appearance:

            return Material(
                name=component.appearance.name
            )

        # -------------------------------------------------
        # Default
        # -------------------------------------------------

        return Material()

    # =====================================================
    # Get Material Dictionary
    # =====================================================

    def parse(self):

        materials = {}

        try:

            for occurrence in self.root.occurrences:

                materials[
                    occurrence.component.name
                ] = self._extract_material(
                    occurrence
                )

        except Exception:

            print(traceback.format_exc())

        return materials