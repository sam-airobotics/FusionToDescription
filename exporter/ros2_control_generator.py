"""
ros2_control_generator.py

Generates ros2_control configuration files.

Files generated:
    - urdf/ros2_control.xacro
    - config/ros2_controllers.yaml
    - config/joint_limits.yaml
"""

from .file_writer import FileWriter


class ROS2ControlGenerator:

    def __init__(self, robot, package_creator):

        self.robot = robot
        self.package = package_creator

        self.writer = FileWriter(
            self.package.package_directory()
        )

    # =====================================================
    # Generate All Files
    # =====================================================

    def generate(self):
        
        # Generate xacro file for ros2_control
        self.writer.write_file(
            "urdf/ros2_control.xacro",
            self._ros2_control_xacro()
        )

        self.writer.write_file(
            "config/ros2_controllers.yaml",
            self._controllers_yaml()
        )

        self.writer.write_file(
            "config/joint_limits.yaml",
            self._joint_limits_yaml()
        )

    # =====================================================
    # ros2_control.xacro
    # =====================================================

    def _ros2_control_xacro(self):
        """Generate ros2_control Xacro file."""
        
        package = self.robot.package_name
        
        xacro = f'''<?xml version=\"1.0\"?>
<robot xmlns:xacro=\"http://www.ros.org/wiki/xacro\">

  <xacro:macro name=\"ros2_control\" params=\"name\">

    <ros2_control name=\"{self.robot.robot_name}_ros2_control\" type=\"system\">
      <hardware>
        <plugin>ros2_control_demo_hardware/DemoSystemHardware</plugin>
      </hardware>
'''

        # Add joints to ros2_control
        for joint in self.robot.joints:
            if joint.joint_type != "fixed":
                xacro += f'''
      <joint name=\"{joint.name}\">
        <command_interface name=\"position\"/>
        <state_interface name=\"position\"/>
        <state_interface name=\"velocity\"/>
      </joint>
'''

        xacro += '''    </ros2_control>

  </xacro:macro>

</robot>
'''
        return xacro

    # =====================================================
    # ros2_controllers.yaml
    # =====================================================

    def _controllers_yaml(self):

        yaml = """controller_manager:
  ros__parameters:

    update_rate: 100

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    joint_trajectory_controller:
      type: joint_trajectory_controller/JointTrajectoryController

joint_trajectory_controller:
  ros__parameters:

    joints:
"""

        for joint in self.robot.joints:

            if joint.joint_type != "fixed":

                yaml += f"      - {joint.name}\n"

        yaml += """

    command_interfaces:
      - position

    state_interfaces:
      - position
      - velocity
"""

        return yaml

    # =====================================================
    # joint_limits.yaml
    # =====================================================

    def _joint_limits_yaml(self):

        yaml = "joint_limits:\n"

        for joint in self.robot.joints:

            if joint.joint_type == "fixed":
                continue

            limits = joint.limits

            yaml += f"""
  {joint.name}:

    has_position_limits: true

    min_position: {limits.get("lower", 0.0)}

    max_position: {limits.get("upper", 0.0)}

    has_velocity_limits: true

    max_velocity: {limits.get("velocity", 0.0)}

    has_acceleration_limits: false

    max_acceleration: 0.0

    has_effort_limits: true

    max_effort: {limits.get("effort", 0.0)}
"""

        return yaml