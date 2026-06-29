"""
robot_xacro_generator.py

Generates the main robot.urdf.xacro file from the RobotModel.

FIXED: Added config parameter for future enhancements
"""

from .file_writer import FileWriter
from .urdf_generator import URDFGenerator
from xml.sax.saxutils import quoteattr


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
        """Generate the main robot Xacro file."""

        xacro = self._build_xacro()

        self.writer.write_file(
            f"urdf/{self.robot.robot_name}.xacro",
            xacro
        )

    # =====================================================
    # Build Robot Xacro
    # =====================================================

    def _build_xacro(self):
        """Build the main Xacro file content."""

        package = self.robot.package_name
        robot_name = self.robot.robot_name

        xacro = f"""<?xml version='1.0' encoding='utf-8'?>
<robot name={quoteattr(robot_name)} xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Include materials -->
  <xacro:include filename="$(find {package})/urdf/materials.xacro"/>
"""

        # ✅ ADDED: Conditional includes based on config
        if self.config and self.config.generate_gazebo:
            xacro += f"""
  <!-- Include gazebo -->
  <xacro:include filename="$(find {package})/urdf/gazebo.xacro"/>
"""

        if self.config and self.config.generate_ros2_control:
            xacro += f"""  <!-- <xacro:include filename="$(find {package})/urdf/ros2_control.xacro"/> -->
"""

        renderer = URDFGenerator(self.robot, self.package, self.config)

        add_base_footprint = self._needs_base_footprint()

        if add_base_footprint:
            xacro += """
    <link name="base_footprint"/>
"""

        for link in self.robot.links:
            xacro += renderer._generate_link(link, xacro=True)

        if add_base_footprint:
            xacro += """
    <joint name="base_joint" type="fixed">
        <origin xyz="0.0 0.0 0.0" rpy="0.0 0.0 0.0" />
        <parent link="base_footprint" />
        <child link="base_link" />
    </joint>
"""

        xacro += "\n<!-- Joints -->\n"

        for joint in self.robot.joints:
            xacro += renderer._generate_joint(joint)

        xacro += """

</robot>
"""

        return xacro

    def _needs_base_footprint(self):
        """Return true when base_link is the root and needs the reference frame."""

        if not self.robot.get_link("base_link") or self.robot.get_link("base_footprint"):
            return False

        return not any(joint.child == "base_link" for joint in self.robot.joints)
