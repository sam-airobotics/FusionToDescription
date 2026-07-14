"""
launch_generator.py

Generates ROS 2 launch files for the exported robot.
"""

from .file_writer import FileWriter


class LaunchGenerator:

    def __init__(self, robot, package_creator):

        self.robot = robot
        self.package = package_creator

        self.writer = FileWriter(
            self.package.package_directory()
        )

    # =====================================================
    # Generate All Launch Files
    # =====================================================

    def generate(self):

        self.writer.write_file(
            "launch/display.launch.py",
            self._display_launch()
        )

        self.writer.write_file(
            "launch/gazebo.launch.py",
            self._gazebo_launch()
        )

        self.writer.write_file(
            "launch/sim.launch.py",
            self._sim_launch()
        )

    # =====================================================
    # RViz Launch
    # =====================================================

    def _display_launch(self):

        package = self.robot.package_name

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
        "{self.robot.robot_name}.xacro"
    )

    robot_description = ParameterValue(
        Command(["xacro ", xacro_file]),
        value_type=str
    )

    return LaunchDescription([

        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[{{"robot_description": robot_description}}],
            output="screen"
        ),

        Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui"
        ),

        Node(
            package="rviz2",
            executable="rviz2",
            arguments=[
                "-d",
                os.path.join(
                    get_package_share_directory(package_name),
                    "rviz",
                    "{self.robot.robot_name}.rviz"
                )
            ]
        )

    ])
'''

    # =====================================================
    # Gazebo Launch
    # =====================================================

    def _gazebo_launch(self):

        package = self.robot.package_name

        return f'''from launch import LaunchDescription

from launch.actions import IncludeLaunchDescription

from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node

from launch.substitutions import Command

from launch_ros.parameter_descriptions import ParameterValue

from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    package_name = "{package}"

    gazebo = IncludeLaunchDescription(

        PythonLaunchDescriptionSource(

            os.path.join(

                get_package_share_directory("ros_gz_sim"),

                "launch",

                "gz_sim.launch.py"

            )

        ),

        launch_arguments={{

            "gz_args": os.path.join(

                get_package_share_directory(package_name),

                "worlds",

                "empty.world"

            )

        }}.items()

    )

    robot_description = ParameterValue(

        Command([

            "xacro ",

            os.path.join(

                get_package_share_directory(package_name),

                "urdf",

                "{self.robot.robot_name}.xacro"

            )

        ]),

        value_type=str

    )

    state_publisher = Node(

        package="robot_state_publisher",

        executable="robot_state_publisher",

        parameters=[{{"robot_description": robot_description}}]

    )

    spawn = Node(

        package="ros_gz_sim",

        executable="create",

        arguments=[

            "-topic", "robot_description",

            "-name", "{self.robot.robot_name}"

        ],

        output="screen"

    )

    return LaunchDescription([

        gazebo,

        state_publisher,

        spawn

    ])
'''

    # =====================================================
    # Full Simulation Launch
    # =====================================================

    def _sim_launch(self):

        package = self.robot.package_name

        return f'''from launch import LaunchDescription

from launch.actions import IncludeLaunchDescription

from launch.launch_description_sources import PythonLaunchDescriptionSource

from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    package_name = "{package}"

    gazebo = IncludeLaunchDescription(

        PythonLaunchDescriptionSource(

            os.path.join(

                get_package_share_directory(package_name),

                "launch",

                "gazebo.launch.py"

            )

        )

    )

    rviz = IncludeLaunchDescription(

        PythonLaunchDescriptionSource(

            os.path.join(

                get_package_share_directory(package_name),

                "launch",

                "display.launch.py"

            )

        )

    )

    return LaunchDescription([

        gazebo,

        rviz

    ])
'''