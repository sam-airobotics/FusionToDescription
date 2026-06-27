"""
display_launch_generator.py

Generates the RViz display launch file.
"""

from .file_writer import FileWriter


class DisplayLaunchGenerator:

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
            "launch/display.launch.py",
            self._build()
        )

    # =====================================================
    # Build Launch File
    # =====================================================

    def _build(self):

        package = self.robot.package_name
        robot = self.robot.robot_name

        return f'''from launch import LaunchDescription

from launch.actions import IncludeLaunchDescription

from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    package_name = "{package}"

    robot_state_publisher = IncludeLaunchDescription(

        PythonLaunchDescriptionSource(

            os.path.join(

                get_package_share_directory(package_name),

                "launch",

                "robot_state_publisher.launch.py"

            )

        )

    )

    rviz = Node(

        package="rviz2",

        executable="rviz2",

        output="screen",

        arguments=[

            "-d",

            os.path.join(

                get_package_share_directory(package_name),

                "rviz",

                "{robot}.rviz"

            )

        ]

    )

    return LaunchDescription([

        robot_state_publisher,

        rviz

    ])
'''