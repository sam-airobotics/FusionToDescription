"""Generate modern Gazebo (gz_ros2_control) control resources for ROS 2 Jazzy."""

from .file_writer import FileWriter


class ROS2ControlGenerator:
    def __init__(self, robot, package_creator, config=None):
        self.robot = robot
        self.package = package_creator
        self.config = config
        self.writer = FileWriter(self.package.package_directory())

    def generate(self):
        self.writer.write_file("config/ros2_control.yaml", self._build_controller_yaml())
        self.writer.write_file("config/controllers.yaml", self._build_controller_yaml())
        self.writer.write_file("urdf/ros2_control.xacro", self._build_control_xacro())
        self.writer.write_file("launch/controllers.launch.py", self._build_controllers_launch())

    def _controlled_joints(self):
        return [joint for joint in self.robot.joints if joint.joint_type in ("revolute", "continuous", "prismatic")]

    def _build_controller_yaml(self):
        joints = self._controlled_joints()
        lines = [
            "# Generated ros2_control controller configuration",
            "controller_manager:",
            "  ros__parameters:",
            "    update_rate: 100",
            "    joint_state_broadcaster:",
            "      type: joint_state_broadcaster/JointStateBroadcaster",
            "    joint_trajectory_controller:",
            "      type: joint_trajectory_controller/JointTrajectoryController",
            "",
            "joint_trajectory_controller:",
            "  ros__parameters:",
            "    joints:",
        ]
        for joint in joints:
            lines.append(f"      - {joint.name}")
        lines += [
            "    command_interfaces:",
            "      - position",
            "    state_interfaces:",
            "      - position",
            "      - velocity",
            "    state_publish_rate: 50.0",
            "    action_monitor_rate: 20.0",
            "    allow_partial_joints_goal: true",
            "",
            "joint_state_broadcaster:",
            "  ros__parameters:",
            "    use_local_topics: false",
            "",
        ]
        return "\n".join(lines)

    def _build_control_xacro(self):
        package = self.robot.package_name
        lines = [
            '<?xml version="1.0"?>',
            '<robot xmlns:xacro="http://www.ros.org/wiki/xacro">',
            '  <ros2_control name="GazeboSimSystem" type="system">',
            '    <hardware>',
            '      <plugin>gz_ros2_control/GazeboSimSystem</plugin>',
            '    </hardware>',
        ]
        for joint in self._controlled_joints():
            lines += [
                f'    <joint name="{joint.name}">',
                '      <command_interface name="position"/>',
                '      <state_interface name="position"/>',
                '      <state_interface name="velocity"/>',
                '    </joint>',
            ]
        lines += [
            '  </ros2_control>',
            '  <gazebo>',
            '    <plugin filename="libgz_ros2_control-system.so" name="gz_ros2_control::GazeboSimROS2ControlPlugin">',
            f'      <parameters>$(find {package})/config/controllers.yaml</parameters>',
            '    </plugin>',
            '  </gazebo>',
            '</robot>',
            '',
        ]
        return "\n".join(lines)

    def _build_controllers_launch(self):
        package = self.robot.package_name
        return f'''"""Spawn controllers for {self.robot.robot_name}."""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    config = PathJoinSubstitution([FindPackageShare("{package}"), "config", "controllers.yaml"])
    joint_state = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--param-file", config],
        output="screen",
    )
    trajectory = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_trajectory_controller", "--param-file", config],
        output="screen",
    )
    return LaunchDescription([joint_state, trajectory])
'''
