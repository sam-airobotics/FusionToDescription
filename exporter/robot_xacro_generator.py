"""
robot_xacro_generator.py

Generates the main robot.urdf.xacro file from the RobotModel.

FIXED: Added config parameter for future enhancements
"""

from .file_writer import FileWriter


class RobotXacroGenerator:

    def __init__(
        self,
        robot,
        package_creator,
        config=None
    ):
        """
        Initialize robot xacro generator.
        
        Args:
            robot: RobotModel instance
            package_creator: PackageCreator instance
            config: ExportConfig instance (optional)
        """

        self.robot = robot
        self.package = package_creator
        self.config = config  # ✅ ADDED: For future conditional generation

        self.writer = FileWriter(
            self.package.package_directory()
        )

    # =====================================================
    # Generate Main Robot Xacro
    # =====================================================

    def generate(self):
        """Generate the main robot.urdf.xacro file."""

        xacro = self._build_xacro()

        self.writer.write_file(
            f"urdf/{self.robot.robot_name}.urdf.xacro",
            xacro
        )

    # =====================================================
    # Build Robot Xacro
    # =====================================================

    def _build_xacro(self):
        """Build the main Xacro file content."""

        package = self.robot.package_name
        robot_name = self.robot.robot_name

        xacro = f"""<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="{robot_name}">

  <!-- ============================= -->
  <!-- Include Sub-Xacro Files      -->
  <!-- ============================= -->

  <xacro:include filename="$(find {package})/urdf/materials.xacro"/>
  <xacro:include filename="$(find {package})/urdf/links.xacro"/>
  <xacro:include filename="$(find {package})/urdf/joints.xacro"/>
"""

        # ✅ ADDED: Conditional includes based on config
        if self.config and self.config.generate_gazebo:
            xacro += f"""  <xacro:include filename="$(find {package})/urdf/gazebo.xacro"/>
"""

        if self.config and self.config.generate_ros2_control:
            xacro += f"""  <!-- <xacro:include filename="$(find {package})/urdf/ros2_control.xacro"/> -->
"""

        xacro += """
  <!-- ============================= -->
  <!-- Root Link (base_link)         -->
  <!-- ============================= -->

  <link name="world"/>

  <joint name="fixed" type="fixed">
    <parent link="world"/>
    <child link="base_link"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </joint>

</robot>
"""

        return xacro
