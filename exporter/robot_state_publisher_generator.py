"""
robot_state_publisher_generator.py

Generates a reusable launch file for the
Robot State Publisher.
"""

from .file_writer import FileWriter


class RobotStatePublisherGenerator:

    def __init__(self, robot, package_creator):

        self.robot = robot
        self.package = package_creator

        self.writer = FileWriter(
            self.package.package_directory()
        )

    # =====================================================
    # Generate
    # =====================================================

    def generate(self):

        self.writer.write_file(
            "launch/robot_state_publisher.launch.py",
            self._build()
        )

    # =====================================================
    # Build Launch File
    # =====================================================

    def _build(self):

        package = self.robot.package_name
        robot = self.robot.robot_name

        return f'''from launch import LaunchDescription

from launch_ros.actions import Node

from launch.substitutions import Command

from launch_ros.parameter_descriptions import ParameterValue

from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    package_name = "{package}"

    xacro_file = os.path.join(
        get_package_share_directory(package_name),
        "urdf",
        "{robot}.xacro"
    )

    robot_description = ParameterValue(
        Command(["xacro", " ", xacro_file]),
        value_type=str
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[
            {{
                "robot_description": robot_description
            }}
        ]
    )

    joint_state_publisher = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        output="screen"
    )

    return LaunchDescription([

        joint_state_publisher,

        robot_state_publisher

    ])
'''