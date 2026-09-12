"""
export_manager.py

Main backend manager for the FusionToDescription exporter.
Coordinates Fusion parsers and ROS package generators.
"""

import os

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
    """Coordinates the complete export pipeline."""

    def __init__(self, config):
        self.config = config

    def _apply_material_colors(self, robot):
        """Apply user-selected visualization colors while preserving material names."""
        Logger.info("Applying user material colors...")
        color_map = {
            "Default": (0.7, 0.7, 0.7, 1.0),
            "White": (1.0, 1.0, 1.0, 1.0),
            "Black": (0.0, 0.0, 0.0, 1.0),
            "Gray": (0.5, 0.5, 0.5, 1.0),
            "Silver": (0.75, 0.75, 0.75, 1.0),
            "Red": (1.0, 0.0, 0.0, 1.0),
            "Green": (0.0, 1.0, 0.0, 1.0),
            "Blue": (0.0, 0.0, 1.0, 1.0),
            "Yellow": (1.0, 1.0, 0.0, 1.0),
            "Orange": (1.0, 0.5, 0.0, 1.0),
            "Purple": (0.6, 0.2, 0.8, 1.0),
        }
        for link in robot.links:
            dropdown = ui_context.get_material_dropdown(link.name)
            if dropdown is None or dropdown.selectedItem is None or link.material is None:
                continue
            selected_color = dropdown.selectedItem.name
            rgba = color_map.get(selected_color, color_map["Default"])
            link.material.color.r = rgba[0]
            link.material.color.g = rgba[1]
            link.material.color.b = rgba[2]
            link.material.color.a = rgba[3]

    @staticmethod
    def _verify_files(package, config):
        required = [
            (package.package_xml_path(), "package.xml"),
            (package.cmake_lists_path(), "CMakeLists.txt"),
            (package.xacro_path(), "robot Xacro"),
        ]
        if config.generate_urdf:
            required.append((package.urdf_path(), "URDF"))
        if config.generate_rviz:
            required.append((package.rviz_config_path(), "RViz configuration"))
        if config.generate_launch:
            required.append((os.path.join(package.launch_directory(), "display.launch.py"), "display launch"))
        missing = [label for path, label in required if not os.path.isfile(path)]
        if missing:
            raise RuntimeError("Export completed with missing artifacts: " + ", ".join(missing))

    def export(self):
        """Run the complete export and propagate failures to the caller."""
        Logger.separator()
        Logger.start("FusionToDescription Export")

        validator = Validator(self.config)
        result = validator.validate()
        if not result["valid"]:
            validator.print_report()
            raise RuntimeError("\n".join(result["errors"]))

        package = PackageCreator(self.config)
        Logger.info(f"Creating ROS package at {package.package_directory()}...")
        package.create()

        Logger.info("Building robot model...")
        robot = RobotModelBuilder(self.config).build()
        if robot is None:
            raise RuntimeError("Failed to build RobotModel.")

        self._apply_material_colors(robot)

        Logger.info("Validating robot model...")
        validator = Validator(self.config, robot)
        result = validator.validate()
        if not result["valid"]:
            validator.print_report()
            raise RuntimeError("\n".join(result["errors"]))

        Logger.info("Generating package metadata...")
        PackageXMLGenerator(robot, package).generate()
        CMakeGenerator(robot, package).generate()

        Logger.info("Generating Xacro files...")
        MaterialsXacroGenerator(robot, package, self.config).generate()
        if self.config.generate_gazebo:
            GazeboPluginXacroGenerator(robot, package, self.config).generate()
        RobotXacroGenerator(robot, package, self.config).generate()

        if self.config.generate_urdf:
            Logger.info("Generating URDF...")
            URDFGenerator(robot, package, self.config).generate()

        if self.config.generate_ros2_control:
            Logger.info("Generating ros2_control...")
            ROS2ControlGenerator(robot, package, self.config).generate()

        if self.config.generate_gazebo:
            Logger.info("Generating Gazebo resources...")
            GazeboGenerator(robot, package, self.config).generate()

        if self.config.generate_rviz:
            Logger.info("Generating RViz configuration...")
            RVizGenerator(robot, package, self.config).generate()

        if self.config.generate_launch:
            Logger.info("Generating launch files...")
            LaunchGenerator(robot, package).generate()

        self._verify_files(package, self.config)
        Logger.info(f"Export artifacts verified in {package.package_directory()}")
        Logger.finish("FusionToDescription Export")
        Logger.separator()
        return robot
