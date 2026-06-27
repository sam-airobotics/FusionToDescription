"""
robot_xacro_generator.py

Generates the main robot Xacro file.
"""

from .file_writer import FileWriter


class RobotXacroGenerator:

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
            f"urdf/{self.robot.robot_name}.xacro",
            self._build()
        )

    # =====================================================
    # Build Xacro
    # =====================================================

    def _build(self):

        package = self.robot.package_name

        xml = f"""<?xml version="1.0"?>

<robot
    xmlns:xacro="http://www.ros.org/wiki/xacro"
    name="{self.robot.robot_name}">

  <!-- Materials -->
  <xacro:include filename="package://{package}/urdf/materials.xacro"/>

  <!-- Links -->
  <xacro:include filename="package://{package}/urdf/links.xacro"/>

  <!-- Joints -->
  <xacro:include filename="package://{package}/urdf/joints.xacro"/>
"""

        # Optional Gazebo plugins
        if getattr(self.robot, "generate_gazebo", False):

            xml += f"""
  <!-- Gazebo Plugins -->
  <xacro:include filename="package://{package}/urdf/gazebo_plugins.xacro"/>
"""

        # Optional ros2_control
        if getattr(self.robot, "generate_control", False):

            xml += f"""
  <!-- ros2_control -->
  <xacro:include filename="package://{package}/urdf/ros2_control.xacro"/>
"""

        xml += """

</robot>
"""

        return xml