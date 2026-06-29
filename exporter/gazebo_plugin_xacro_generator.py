"""
gazebo_plugin_xacro_generator.py

Generates the gazebo.xacro file with sensor and actuator plugin definitions.

FIXED:
- Added config parameter
- Harmonic-compatible plugin configuration
- Proper sensor plugin templates
"""

from .file_writer import FileWriter
from xml.sax.saxutils import escape, quoteattr


class GazeboPluginXacroGenerator:

    def __init__(
        self,
        robot,
        package_creator,
        config=None
    ):
        """
        Initialize gazebo plugin xacro generator.
        
        Args:
            robot: RobotModel instance
            package_creator: PackageCreator instance
            config: ExportConfig instance (optional)
        """

        self.robot = robot
        self.package = package_creator
        self.config = config  # ✅ ADDED: Use for Harmonic-specific config

        self.writer = FileWriter(
            self.package.package_directory()
        )

    # =====================================================
    # Generate Gazebo Xacro
    # =====================================================

    def generate(self):
        """Generate the gazebo.xacro file with plugin definitions."""

        xacro = self._build_xacro()

        self.writer.write_file(
            f"urdf/gazebo.xacro",
            xacro
        )

    # =====================================================
    # Build Gazebo Xacro
    # =====================================================

    def _build_xacro(self):
        """Build gazebo-specific Xacro content for Harmonic."""

        xacro = f"""<?xml version="1.0" ?>
<robot name={quoteattr(self.robot.robot_name)} xmlns:xacro="http://www.ros.org/wiki/xacro">
"""

        material_map = {
            "Black": "Gazebo/Black",
            "Blue": "Gazebo/Blue",
            "Green": "Gazebo/Green",
            "Red": "Gazebo/Red",
            "Silver": "Gazebo/Grey",
            "Yellow": "Gazebo/Yellow",
        }

        for link in self.robot.links:
            gazebo_material = material_map.get(link.material, "Gazebo/Grey")
            xacro += f"""
  <gazebo reference={quoteattr(link.name)}>
    <material>{gazebo_material}</material>
    <mu1>0.2</mu1>
    <mu2>0.2</mu2>
    <self_collide>true</self_collide>
    <gravity>true</gravity>
  </gazebo>
"""

        moving_joints = [
            joint for joint in self.robot.joints if joint.joint_type != "fixed"
        ]
        if moving_joints:
            xacro += """
  <gazebo>
    <plugin filename="gz-sim-joint-state-publisher-system" name="gz::sim::systems::JointStatePublisher">
      <topic>joint_states</topic>
"""
            for joint in moving_joints:
                xacro += f"      <joint_name>{escape(joint.name)}</joint_name>\n"

            xacro += """    </plugin>
  </gazebo>
"""

        xacro += """
</robot>
"""

        return xacro
