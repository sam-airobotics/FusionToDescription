"""
package_creator.py

Creates the directory structure for a ROS 2 robot
description package.
"""

import os

from .file_writer import FileWriter


class PackageCreator:

    def __init__(self, config):

        self.config = config

        self.robot_name = config.robot_name
        self.package_name = config.package_name
        self.export_path = config.export_directory

        self.writer = FileWriter(self.export_path)

    # =====================================================
    # Create Package Structure
    # =====================================================

    def create(self):

        package_root = self.writer.create_directory(
            self.package_name
        )

        folders = [

            "config",
            "launch",
            "meshes",
            "rviz",
            "urdf",
            "worlds"

        ]

        for folder in folders:

            self.writer.create_directory(
                self.package_name,
                folder
            )

        return self

    # =====================================================
    # Package Paths
    # =====================================================

    def package_directory(self):

        return os.path.join(
            self.export_path,
            self.package_name
        )

    def config_directory(self):

        return os.path.join(
            self.package_directory(),
            "config"
        )

    def launch_directory(self):

        return os.path.join(
            self.package_directory(),
            "launch"
        )

    def meshes_directory(self):

        return os.path.join(
            self.package_directory(),
            "meshes"
        )

    def rviz_directory(self):

        return os.path.join(
            self.package_directory(),
            "rviz"
        )

    def urdf_directory(self):

        return os.path.join(
            self.package_directory(),
            "urdf"
        )

    def worlds_directory(self):

        return os.path.join(
            self.package_directory(),
            "worlds"
        )

    # =====================================================
    # File Paths
    # =====================================================

    def package_xml_path(self):

        return os.path.join(
            self.package_directory(),
            "package.xml"
        )

    def cmake_lists_path(self):

        return os.path.join(
            self.package_directory(),
            "CMakeLists.txt"
        )

    def urdf_path(self):

        return os.path.join(
            self.urdf_directory(),
            f"{self.robot_name}.urdf"
        )

    def xacro_path(self):

        return os.path.join(
            self.urdf_directory(),
            f"{self.robot_name}.xacro"
        )

    def rviz_config_path(self):

        return os.path.join(
            self.rviz_directory(),
            f"{self.robot_name}.rviz"
        )

    def controllers_yaml_path(self):

        return os.path.join(
            self.config_directory(),
            "ros2_controllers.yaml"
        )

    def joint_limits_yaml_path(self):

        return os.path.join(
            self.config_directory(),
            "joint_limits.yaml"
        )