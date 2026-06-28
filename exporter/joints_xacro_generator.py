"""
joints_xacro_generator.py

Generates the joints.xacro file containing all robot joint definitions.

FIXED: Added config parameter for future enhancements
"""

from .file_writer import FileWriter


class JointsXacroGenerator:

    def __init__(
        self,
        robot,
        package_creator,
        config=None
    ):
        """
        Initialize joints xacro generator.
        
        Args:
            robot: RobotModel instance
            package_creator: PackageCreator instance
            config: ExportConfig instance (optional)
        """

        self.robot = robot
        self.package = package_creator
        self.config = config  # ✅ ADDED

        self.writer = FileWriter(
            self.package.package_directory()
        )

    # =====================================================
    # Generate Joints Xacro
    # =====================================================

    def generate(self):
        """Generate the joints.xacro file."""

        xacro = self._build_xacro()

        self.writer.write_file(
            f"urdf/joints.xacro",
            xacro
        )

    # =====================================================
    # Build Joints Xacro
    # =====================================================

    def _build_xacro(self):
        """Build joints xacro content."""

        xacro = f"""<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="{self.robot.robot_name}">

  <!-- ============================= -->
  <!-- Joint Definitions             -->
  <!-- ============================= -->
"""

        for joint in self.robot.joints:
            xacro += self._generate_joint(joint)

        xacro += """
</robot>
"""

        return xacro

    # =====================================================
    # Generate Individual Joint
    # =====================================================

    def _generate_joint(self, joint):
        """Generate Xacro for a single joint."""

        origin = joint.origin
        axis = joint.axis

        xml = f"""
  <joint name="{joint.name}" type="{joint.joint_type}">
    <parent link="{joint.parent}"/>
    <child link="{joint.child}"/>
    <origin xyz="{origin.get('x',0)} {origin.get('y',0)} {origin.get('z',0)}" 
            rpy="{origin.get('roll',0)} {origin.get('pitch',0)} {origin.get('yaw',0)}"/>
"""

        if joint.joint_type != "fixed":
            xml += f"""    <axis xyz="{axis.get('x',0)} {axis.get('y',0)} {axis.get('z',1)}"/>
"""

            limits = joint.limits
            xml += f"""    <limit lower="{limits.get('lower',0)}" 
            upper="{limits.get('upper',0)}" 
            effort="{limits.get('effort',0)}" 
            velocity="{limits.get('velocity',0)}"/>
"""

        xml += """  </joint>
"""

        return xml
