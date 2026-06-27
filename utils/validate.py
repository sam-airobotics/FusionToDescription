"""
validate.py

Validation utilities for FusionToDescription.

Performs pre-export validation on the export configuration
and the generated RobotModel.
"""

import os


class Validator:

    def __init__(self, config, robot=None):

        self.config = config
        self.robot = robot

        self.errors = []
        self.warnings = []

    # =====================================================
    # Main Validation
    # =====================================================

    def validate(self):

        self.errors.clear()
        self.warnings.clear()

        self._validate_config()

        if self.robot is not None:
            self._validate_robot()

        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings
        }

    # =====================================================
    # Configuration Validation
    # =====================================================

    def _validate_config(self):

        if not self.config.robot_name:
            self.errors.append(
                "Robot name cannot be empty."
            )

        if not self.config.export_directory:
            self.errors.append(
                "Export directory is not specified."
            )

        elif not os.path.isdir(self.config.export_directory):
            self.errors.append(
                f"Export directory does not exist: "
                f"{self.config.export_directory}"
            )

        if self.config.mesh_format.lower() not in (
            "stl",
            "obj"
        ):
            self.errors.append(
                f"Unsupported mesh format: "
                f"{self.config.mesh_format}"
            )

    # =====================================================
    # Robot Model Validation
    # =====================================================

    def _validate_robot(self):

        self._validate_links()
        self._validate_joints()

    # =====================================================
    # Links
    # =====================================================

    def _validate_links(self):

        if not self.robot.links:

            self.errors.append(
                "No links were found."
            )

            return

        names = set()

        for link in self.robot.links:

            if link.name in names:

                self.errors.append(
                    f"Duplicate link: {link.name}"
                )

            names.add(link.name)

            if link.mass < 0:

                self.warnings.append(
                    f"Negative mass for link "
                    f"{link.name}"
                )

            if not link.mesh:

                self.warnings.append(
                    f"No mesh assigned to "
                    f"{link.name}"
                )

    # =====================================================
    # Joints
    # =====================================================

    def _validate_joints(self):

        names = set()

        link_names = {
            link.name for link in self.robot.links
        }

        for joint in self.robot.joints:

            if joint.name in names:

                self.errors.append(
                    f"Duplicate joint: {joint.name}"
                )

            names.add(joint.name)

            if joint.parent not in link_names:

                self.errors.append(
                    f"Joint '{joint.name}' "
                    f"references unknown parent "
                    f"'{joint.parent}'"
                )

            if joint.child not in link_names:

                self.errors.append(
                    f"Joint '{joint.name}' "
                    f"references unknown child "
                    f"'{joint.child}'"
                )

            if joint.parent == joint.child:

                self.errors.append(
                    f"Joint '{joint.name}' "
                    f"connects a link to itself."
                )

    # =====================================================
    # Results
    # =====================================================

    def is_valid(self):

        return len(self.errors) == 0

    def print_report(self):

        print("\n========== Validation Report ==========\n")

        if self.errors:

            print("Errors:")

            for error in self.errors:
                print(f"  ✗ {error}")

        else:

            print("No validation errors.")

        if self.warnings:

            print("\nWarnings:")

            for warning in self.warnings:
                print(f"  ! {warning}")

        print("\n=======================================\n")