"""
export_manager.py

Main backend manager for the FusionToDescription exporter.

Coordinates Fusion parsers and ROS package generators.
"""

from ..fusion.robot_model import RobotModelBuilder

from ..utils.logger import Logger
from ..utils.validate import Validator

from .package_creator import PackageCreator
from .package_xml_generator import PackageXMLGenerator
from .cmake_generator import CMakeGenerator
from .urdf_generator import URDFGenerator

from .robot_xacro_generator import RobotXacroGenerator
from .materials_xacro_generator import MaterialsXacroGenerator
from .gazebo_plugin_xacro_generator import GazeboPluginXacroGenerator

from .launch_generator import LaunchGenerator

from .gazebo_generator import GazeboGenerator
from .rviz_generator import RVizGenerator
from .ros2_control_generator import ROS2ControlGenerator

from ..commands.ui import ui_context


class ExportManager:
    """
    Coordinates the complete export pipeline.
    """

    def __init__(self, config):

        self.config = config

    # =====================================================
    # Apply Material Colors
    # =====================================================

    def _apply_material_colors(self, robot):

        Logger.info(
            "Applying user material colors..."
        )

        for link in robot.links:

            picker = ui_context.get_material_color(
                link.name
            )

            if picker is None:
                continue

            color = picker.value

            if color is None:
                continue

            if link.material is None:
                continue

            link.material.color.r = color.red / 255.0
            link.material.color.g = color.green / 255.0
            link.material.color.b = color.blue / 255.0
            link.material.color.a = color.opacity / 255.0

            Logger.info(
                f"{link.name} → {link.material.name}"
            )

    # =====================================================
    # Export
    # =====================================================

    def export(self):

        try:

            Logger.separator()
            Logger.start("FusionToDescription Export")

            # -------------------------------------------------
            # Validate Configuration
            # -------------------------------------------------

            Logger.info("Validating export configuration...")

            validator = Validator(self.config)

            result = validator.validate()

            if not result["valid"]:

                validator.print_report()

                raise RuntimeError(
                    "\n".join(result["errors"])
                )

            # -------------------------------------------------
            # Create Package
            # -------------------------------------------------

            Logger.info("Creating ROS package...")

            package = PackageCreator(self.config)

            package.create()

            # -------------------------------------------------
            # Build Robot Models
            # -------------------------------------------------

            Logger.info("Building robot model...")

            builder = RobotModelBuilder(self.config)

            robot = builder.build()

            if robot is None:

                raise RuntimeError(
                    "Failed to build RobotModel."
                )
            
            # ---------------------------------------------
            # Apply User Material Colors
            # ---------------------------------------------

            self._apply_material_colors(robot)

            # -------------------------------------------------
            # Validate Robot Model
            # -------------------------------------------------

            Logger.info("Validating robot model...")

            validator = Validator(
                self.config,
                robot
            )

            result = validator.validate()

            if not result["valid"]:

                validator.print_report()

                raise RuntimeError(
                    "\n".join(result["errors"])
                )

            # -------------------------------------------------
            # Core Package Files
            # -------------------------------------------------

            Logger.info("Generating package files...")

            PackageXMLGenerator(
                robot,
                package
            ).generate()

            CMakeGenerator(
                robot,
                package
            ).generate()

            # -------------------------------------------------
            # Xacro Files
            # -------------------------------------------------

            Logger.info("Generating Xacro files...")

            MaterialsXacroGenerator(
                robot,
                package,
                self.config
            ).generate()

            if self.config.generate_gazebo:

                GazeboPluginXacroGenerator(
                    robot,
                    package,
                    self.config
                ).generate()

            if self.config.generate_ros2_control:

                # Future:
                # ROS2ControlXacroGenerator(
                #     robot,
                #     package
                # ).generate()
                pass

            RobotXacroGenerator(
                robot,
                package,
                self.config
            ).generate()

            # -------------------------------------------------
            # Optional URDF
            # -------------------------------------------------

            if self.config.generate_urdf:

                Logger.info("Generating URDF...")

                URDFGenerator(
                    robot,
                    package,
                    self.config
                ).generate()

            # -------------------------------------------------
            # ros2_control
            # -------------------------------------------------

            if self.config.generate_ros2_control:

                Logger.info("Generating ros2_control...")

                ROS2ControlGenerator(
                    robot,
                    package,
                    self.config
                ).generate()

            # -------------------------------------------------
            # Gazebo
            # -------------------------------------------------

            if self.config.generate_gazebo:

                Logger.info("Generating Gazebo resources...")

                GazeboGenerator(
                    robot,
                    package,
                    self.config
                ).generate()

            # -------------------------------------------------
            # RViz
            # -------------------------------------------------

            if self.config.generate_rviz:

                Logger.info("Generating RViz configuration...")

                RVizGenerator(
                    robot,
                    package,
                    self.config
                ).generate()

            # -------------------------------------------------
            # Launch Files
            # -------------------------------------------------

            if self.config.generate_launch:

                Logger.info("Generating launch files...")

                LaunchGenerator(
                    robot,
                    package
                ).generate()

            Logger.finish("FusionToDescription Export")
            Logger.separator()

            return robot

        except Exception as error:

            Logger.exception(error)

            return None
