"""
transform_parser.py

Extracts component transforms from the active
Fusion 360 design.

Each transform is returned as a translation and
rotation matrix for later conversion to URDF.
"""

import traceback

import adsk.core
import adsk.fusion


app = adsk.core.Application.get()


class TransformParser:

    def __init__(self):

        self.design = app.activeProduct

        if not isinstance(self.design, adsk.fusion.Design):
            raise RuntimeError(
                "No active Fusion Design."
            )

        self.root = self.design.rootComponent

    # =====================================================
    # Parse All Component Transforms
    # =====================================================

    def parse(self):

        transforms = {}

        try:

            for occurrence in self.root.occurrences:

                transforms[
                    occurrence.component.name
                ] = self._parse_transform(
                    occurrence
                )

        except Exception as e:
            print(f"Error parsing transforms: {str(e)}")
            print(traceback.format_exc())

        return transforms

    # =====================================================
    # Parse Single Transform
    # =====================================================

    def _parse_transform(self, occurrence):

        matrix = occurrence.transform2

        translation = matrix.translation

        return {

            "translation": {

                "x": translation.x,
                "y": translation.y,
                "z": translation.z

            },

            "rotation": {

                "r11": matrix.getCell(0, 0),
                "r12": matrix.getCell(0, 1),
                "r13": matrix.getCell(0, 2),

                "r21": matrix.getCell(1, 0),
                "r22": matrix.getCell(1, 1),
                "r23": matrix.getCell(1, 2),

                "r31": matrix.getCell(2, 0),
                "r32": matrix.getCell(2, 1),
                "r33": matrix.getCell(2, 2)

            }

        }