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
        robot_xacro = f"{self.robot.robot_name}.xacro"
        return f'''from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    package_name = "{package}"
    use_gui = LaunchConfiguration("use_gui", default="false")

    description_file = PathJoinSubstitution([
        FindPackageShare(package_name), "urdf", "{robot_xacro}"
    ])
    robot_description = ParameterValue(
        Command([FindExecutable(name="xacro"), " ", description_file]),
        value_type=str,
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{{"robot_description": robot_description}}],
    )

    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        output="screen",
        condition=None,
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", PathJoinSubstitution([
            FindPackageShare(package_name), "rviz", "{self.robot.robot_name}.rviz"
        ])],
    )

    return LaunchDescription([
        DeclareLaunchArgument("use_gui", default_value="false"),
        robot_state_publisher,
        joint_state_publisher,
        rviz,
    ])
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
    xacro_file = PathJoinSubstitution([share, "urdf", "{self.robot.robot_name}.xacro"])
    robot_description = ParameterValue(
        Command([FindExecutable(name="xacro"), " ", xacro_file]),
        value_type=str,
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("ros_gz_sim"),
                "launch", "gz_sim.launch.py"
            )
        ),
        launch_arguments={{"gz_args": PathJoinSubstitution([share, "worlds", "empty.sdf"])}.perform(None) if False else "-r -v 4"}.items(),
    )

    state_publisher = Node(
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

    return LaunchDescription([gazebo, state_publisher, spawn])
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
    package_name = "{package}"
    share = get_package_share_directory(package_name)
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
