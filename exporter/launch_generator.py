"""
launch_generator.py

Generates ROS 2 launch files for the exported robot.
"""

from .file_writer import FileWriter


class LaunchGenerator:
    def __init__(self, robot, package_creator):
        self.robot = robot
        self.package = package_creator
        self.writer = FileWriter(self.package.package_directory())

    def generate(self):
        self.writer.write_file("launch/display.launch.py", self._display_launch())
        self.writer.write_file("launch/gazebo.launch.py", self._gazebo_launch())
        self.writer.write_file("launch/sim.launch.py", self._sim_launch())

    def _display_launch(self):
        package = self.robot.package_name
        return f'''from launch import LaunchDescription
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    package_name = "{package}"
    share = FindPackageShare(package_name)
    description_file = PathJoinSubstitution([share, "urdf", "{self.robot.robot_name}.xacro"])
    rviz_file = PathJoinSubstitution([share, "rviz", "{self.robot.robot_name}.rviz"])

    robot_description = ParameterValue(
        Command([FindExecutable(name="xacro"), " ", description_file]),
        value_type=str,
    )

    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{{"robot_description": robot_description}}],
    )
    jsp = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        output="screen",
    )
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_file],
    )

    return LaunchDescription([rsp, jsp, rviz])
'''

    def _gazebo_launch(self):
        package = self.robot.package_name
        return f'''from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    package_name = "{package}"
    share = FindPackageShare(package_name)
    description_file = PathJoinSubstitution([share, "urdf", "{self.robot.robot_name}.xacro"])
    world_file = PathJoinSubstitution([share, "worlds", "empty.sdf"])

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("ros_gz_sim"),
                "launch",
                "gz_sim.launch.py",
            )
        ),
        launch_arguments={{"gz_args": [world_file]}}.items(),
    )

    robot_description = ParameterValue(
        Command([FindExecutable(name="xacro"), " ", description_file]),
        value_type=str,
    )
    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{{"robot_description": robot_description, "use_sim_time": True}}],
    )
    spawn = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=["-topic", "robot_description", "-name", "{self.robot.robot_name}"],
        output="screen",
    )
    return LaunchDescription([gazebo, rsp, spawn])
'''

    def _sim_launch(self):
        package = self.robot.package_name
        return f'''from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    share = get_package_share_directory("{package}")
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(share, "launch", "gazebo.launch.py"))
    )
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", os.path.join(share, "rviz", "{self.robot.robot_name}.rviz")],
        parameters=[{{"use_sim_time": True}}],
    )
    return LaunchDescription([gazebo, rviz])
'''
