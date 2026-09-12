"""Main backend manager for the FusionToDescription exporter."""

import os
from xml.etree import ElementTree as ET

from ..commands.ui import ui_context
from ..fusion.robot_model import RobotModelBuilder
from ..utils.logger import Logger
from ..utils.validate import Validator
from .cmake_generator import CMakeGenerator
from .gazebo_generator import GazeboGenerator
from .gazebo_plugin_xacro_generator import GazeboPluginXacroGenerator
from .joints_xacro_generator import JointsXacroGenerator
from .launch_generator import LaunchGenerator
from .materials_xacro_generator import MaterialsXacroGenerator
from .package_creator import PackageCreator
from .package_xml_generator import PackageXMLGenerator
from .robot_xacro_generator import RobotXacroGenerator
from .ros2_control_generator import ROS2ControlGenerator
from .rviz_generator import RVizGenerator
from .urdf_generator import URDFGenerator


class ExportManager:
    """Coordinate model extraction, package generation and post-export validation."""

    def __init__(self, config):
        self.config = config

    def _apply_material_colors(self, robot):
        # Preserve the user-selected named color without replacing extracted colors
        # unless the UI explicitly selected a material for this occurrence.
        color_map = {
            "Default": (0.7, 0.7, 0.7, 1.0), "White": (1.0, 1.0, 1.0, 1.0),
            "Black": (0.0, 0.0, 0.0, 1.0), "Gray": (0.5, 0.5, 0.5, 1.0),
            "Silver": (0.75, 0.75, 0.75, 1.0), "Red": (1.0, 0.0, 0.0, 1.0),
            "Green": (0.0, 1.0, 0.0, 1.0), "Blue": (0.0, 0.0, 1.0, 1.0),
            "Yellow": (1.0, 1.0, 0.0, 1.0), "Orange": (1.0, 0.5, 0.0, 1.0),
            "Purple": (0.6, 0.2, 0.8, 1.0),
        }
        for link in robot.links:
            dropdown = ui_context.get_material_dropdown(link.name)
            if dropdown is None or dropdown.selectedItem is None or link.material is None:
                continue
            name = dropdown.selectedItem.name
            rgba = color_map.get(name)
            if rgba:
                link.material.color.r, link.material.color.g = rgba[0], rgba[1]
                link.material.color.b, link.material.color.a = rgba[2], rgba[3]

    def _verify_files(self, package):
        required = [
            (package.package_xml_path(), "package.xml"),
            (package.cmake_lists_path(), "CMakeLists.txt"),
            (package.xacro_path(), "robot Xacro"),
        ]
        if self.config.generate_urdf:
            required.append((package.urdf_path(), "URDF"))
        if self.config.generate_rviz:
            required.append((package.rviz_config_path(), "RViz configuration"))
        if self.config.generate_launch:
            required.extend((
                (os.path.join(package.launch_directory(), "display.launch.py"), "display launch"),
                (os.path.join(package.launch_directory(), "gazebo.launch.py"), "gazebo launch"),
                (os.path.join(package.launch_directory(), "sim.launch.py"), "simulation launch"),
            ))
        if self.config.generate_gazebo:
            required.extend((
                (os.path.join(package.worlds_directory(), "empty.sdf"), "Gazebo world"),
                (os.path.join(package.config_directory(), "bridge_config.yaml"), "bridge config"),
            ))
        if self.config.generate_ros2_control:
            required.extend((
                (os.path.join(package.urdf_directory(), "ros2_control.xacro"), "ros2_control Xacro"),
                (os.path.join(package.config_directory(), "controllers.yaml"), "controllers YAML"),
                (os.path.join(package.launch_directory(), "controllers.launch.py"), "controllers launch"),
            ))

        missing = [label for path, label in required if not os.path.isfile(path) or os.path.getsize(path) == 0]
        if missing:
            raise RuntimeError("Export completed with missing/empty artifacts: " + ", ".join(missing))

        for path, _label in required:
            if path.lower().endswith((".xml", ".urdf", ".xacro", ".sdf")):
                try:
                    ET.parse(path)
                except ET.ParseError as exc:
                    raise RuntimeError(f"Generated XML is invalid: {path}: {exc}") from exc

    def export(self):
        Logger.separator()
        Logger.start("FusionToDescription Export")
        config_result = Validator(self.config).validate()
        if not config_result["valid"]:
            raise RuntimeError("\n".join(config_result["errors"]))

        package = PackageCreator(self.config)
        package.create()
        Logger.info(f"Creating ROS package at {package.package_directory()}...")

        robot = RobotModelBuilder(self.config).build()
        if robot is None:
            raise RuntimeError("Failed to build RobotModel.")
        self._apply_material_colors(robot)

        validation = Validator(self.config, robot)
        result = validation.validate()
        if not result["valid"]:
            validation.print_report()
            raise RuntimeError("\n".join(result["errors"]))

        PackageXMLGenerator(robot, package).generate()
        CMakeGenerator(robot, package).generate()
        MaterialsXacroGenerator(robot, package, self.config).generate()
        JointsXacroGenerator(robot, package, self.config).generate()
        RobotXacroGenerator(robot, package, self.config).generate()
        if self.config.generate_gazebo:
            GazeboPluginXacroGenerator(robot, package, self.config).generate()
            GazeboGenerator(robot, package, self.config).generate()
        if self.config.generate_ros2_control:
            ROS2ControlGenerator(robot, package, self.config).generate()
        if self.config.generate_urdf:
            URDFGenerator(robot, package, self.config).generate()
        if self.config.generate_rviz:
            RVizGenerator(robot, package, self.config).generate()
        if self.config.generate_launch:
            LaunchGenerator(robot, package).generate()

        self._verify_files(package)
        Logger.info(f"Export artifacts verified in {package.package_directory()}")
        Logger.finish("FusionToDescription Export")
        Logger.separator()
        return robot
