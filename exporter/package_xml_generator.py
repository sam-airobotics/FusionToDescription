"""
package_xml_generator.py

Generates package.xml for a ROS 2 robot description package.
Target:
    - ROS 2 Jazzy
    - Gazebo Harmonic
"""

from .file_writer import FileWriter
from xml.sax.saxutils import escape, quoteattr


class PackageXMLGenerator:

    def __init__(
        self,
        robot,
        package_creator
    ):

        self.robot = robot
        self.package = package_creator

        self.writer = FileWriter(
            self.package.package_directory()
        )

    # =====================================================
    # Generate package.xml
    # =====================================================

    def generate(self):

        xml = self._build_xml()

        self.writer.write_file(
            "package.xml",
            xml
        )

    # =====================================================
    # Build XML
    # =====================================================

    def _build_xml(self):

        dependencies = self._dependencies()
        config = self.package.config
        maintainer_name = config.maintainer_name or "TODO"
        maintainer_email = config.maintainer_email or "user@example.com"

        xml = f"""<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>{escape(self.robot.package_name)}</name>
  <version>{escape(config.package_version)}</version>
  <description>{escape(config.description)}</description>
  <maintainer email={quoteattr(maintainer_email)}>{escape(maintainer_name)}</maintainer>
  <license>{escape(config.license)}</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

{dependencies}
  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
"""

        return xml

    # =====================================================
    # Dependencies
    # =====================================================

    def _dependencies(self):

        deps = [

"robot_state_publisher",
"joint_state_publisher",
"joint_state_publisher_gui",
"rviz2",
"xacro",
"urdf"

        ]

        # Gazebo Harmonic

        if self.package.config.generate_gazebo:

            deps.extend([
"ros_gz_sim",
"ros_gz_bridge"
            ])

        # ros2_control

        if self.package.config.generate_ros2_control:

            deps.extend([
"controller_manager",
"joint_state_broadcaster",
"joint_trajectory_controller",
"ros2_control",
"ros2_controllers"
            ])

        xml = ""

        for dep in sorted(set(deps)):

            xml += f"  <depend>{dep}</depend>\n"

        return xml
