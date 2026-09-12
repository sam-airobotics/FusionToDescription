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
        if self.config and self.config.generate_ros2_control:
            xacro += f'  <xacro:include filename="$(find {package})/urdf/ros2_control.xacro"/>\n'

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
        # Keep all joints in one source of truth. This avoids the old duplicated
        # joint definitions in joints.xacro and the main Xacro.
        xacro += '\n  <xacro:include filename="$(find ' + package + ')/urdf/joints.xacro"/>\n'
        xacro += '\n</robot>\n'
        return xacro

    def _needs_base_footprint(self):
        if self.robot.get_link("base_link") is None or self.robot.get_link("base_footprint") is not None:
            return False
        return not any(joint.child == "base_link" for joint in self.robot.joints)
