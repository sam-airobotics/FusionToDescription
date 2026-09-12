"""Generate ROS 2 package.xml metadata."""

from .file_writer import FileWriter
from xml.sax.saxutils import escape, quoteattr


class PackageXMLGenerator:
    def __init__(self, robot, package_creator):
        self.robot = robot
        self.package = package_creator
        self.writer = FileWriter(self.package.package_directory())

    def generate(self):
        return self.writer.write_file("package.xml", self._build_xml())

    def _build_xml(self):
        config = self.package.config
        maintainer_name = config.maintainer_name.strip() or "FusionToDescription"
        maintainer_email = config.maintainer_email.strip() or "noreply@example.com"
        deps = {
            "robot_state_publisher", "joint_state_publisher", "rviz2", "xacro", "urdf"
        }
        if config.generate_gazebo:
            deps.update({"ros_gz_sim", "ros_gz_bridge", "gz_ros2_control"})
        if config.generate_ros2_control:
            deps.update({"controller_manager", "joint_state_broadcaster", "joint_trajectory_controller", "control_msgs", "ros2_control"})

        dep_xml = "\n".join(f"  <depend>{dep}</depend>" for dep in sorted(deps))
        return f'''<?xml version="1.0"?>
<package format="3">
  <name>{escape(self.robot.package_name)}</name>
  <version>{escape(config.package_version)}</version>
  <description>{escape(config.description)}</description>
  <maintainer email={quoteattr(maintainer_email)}>{escape(maintainer_name)}</maintainer>
  <license>{escape(config.license)}</license>

  <buildtool_depend>ament_cmake</buildtool_depend>
{dep_xml}

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
'''
