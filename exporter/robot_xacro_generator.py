"""Generate the main Xacro robot description."""

from xml.sax.saxutils import quoteattr

from .file_writer import FileWriter
from .urdf_generator import URDFGenerator


class RobotXacroGenerator:
    def __init__(self, robot, package_creator, config=None):
        self.robot = robot
        self.package = package_creator
        self.config = config
        self.writer = FileWriter(self.package.package_directory())

    def generate(self):
        return self.writer.write_file(f"urdf/{self.robot.robot_name}.xacro", self._build_xacro())

    def _build_xacro(self):
        package = self.robot.package_name
        renderer = URDFGenerator(self.robot, self.package, self.config)
        xacro = f'''<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name={quoteattr(self.robot.robot_name)}>
  <xacro:include filename="$(find {package})/urdf/materials.xacro"/>
'''
        if self.config and self.config.generate_gazebo:
            xacro += f'  <xacro:include filename="$(find {package})/urdf/gazebo.xacro"/>\n'

        if self._needs_base_footprint():
            xacro += '''
  <link name="base_footprint"/>
  <joint name="base_footprint_joint" type="fixed">
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <parent link="base_footprint"/>
    <child link="base_link"/>
  </joint>
'''

        for link in self.robot.links:
            xacro += renderer._generate_link(link, xacro=True)

        # Generate ros2_control directly inside the main robot so all root-level
        # URDF tags are guaranteed to live under the same <robot> element.
        if self.config and self.config.generate_ros2_control:
            xacro += f'''\n  <ros2_control name="GazeboSimSystem" type="system">
    <hardware>
      <plugin>gz_ros2_control/GazeboSimSystem</plugin>
    </hardware>
'''
            for joint in self.robot.joints:
                if joint.joint_type != "fixed":
                    xacro += f'''    <joint name="{joint.name}">
      <command_interface name="position"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>
'''
            xacro += '''  </ros2_control>
'''

        # Keep joint definitions in one file and include that fragment inside
        # the same robot element.
        xacro += f'  <xacro:include filename="$(find {package})/urdf/joints.xacro"/>\n'

        if self.config and self.config.generate_ros2_control:
            xacro += '''  <gazebo>
    <plugin filename="libgz_ros2_control-system.so" name="gz_ros2_control::GazeboSimROS2ControlPlugin">
      <parameters>$(find ''' + package + ''')/config/controllers.yaml</parameters>
    </plugin>
  </gazebo>
'''

        return xacro + '</robot>\n'

    def _needs_base_footprint(self):
        if self.robot.get_link("base_link") is None or self.robot.get_link("base_footprint") is not None:
            return False
        return not any(joint.child == "base_link" for joint in self.robot.joints)
