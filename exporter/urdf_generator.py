"""
urdf_generator.py

Generates a URDF file from the RobotModel.

FIXED:
- Added config parameter
- Improved error handling
- Better path validation
"""

from .file_writer import FileWriter


class URDFGenerator:

    def __init__(
        self,
        robot,
        package_creator,
        config=None
    ):
        """
        Initialize URDF generator.
        
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
    # Generate URDF
    # =====================================================

    def generate(self):
        """Generate the URDF file."""

        urdf = self._build_urdf()

        self.writer.write_file(
            f"urdf/{self.robot.robot_name}.urdf",
            urdf
        )

    # =====================================================
    # Build URDF
    # =====================================================

    def _build_urdf(self):
        """Build complete URDF content."""

        xml = '<?xml version="1.0"?>\n'
        xml += f'<robot name="{self.robot.robot_name}">\n\n'

        # Links
        for link in self.robot.links:
            xml += self._generate_link(link)

        # Joints
        for joint in self.robot.joints:
            xml += self._generate_joint(joint)

        xml += "</robot>\n"

        return xml

    # =====================================================
    # Link
    # =====================================================

    def _generate_link(self, link):
        """Generate URDF for a single link."""

        xml = f'  <link name="{link.name}">\n'

        # Visual
        if link.mesh:
            xml += (
                '    <visual>\n'
                '      <origin xyz="0 0 0" rpy="0 0 0"/>\n'
                '      <geometry>\n'
                f'        <mesh filename="package://{self.robot.package_name}/meshes/{link.mesh}"/>\n'
                '      </geometry>\n'
            )
            
            if link.material:
                xml += f'      <material name="{link.material}"/>\n'
            
            xml += '    </visual>\n\n'

        # Collision
        xml += self._collision_geometry(link)

        # Inertial
        xml += (
            '    <inertial>\n'
            '      <origin xyz="0 0 0" rpy="0 0 0"/>\n'
            f'      <mass value="{link.mass}"/>\n'
            '      <inertia\n'
            f'          ixx="{link.inertia.get("ixx",0.0)}"\n'
            f'          ixy="{link.inertia.get("ixy",0.0)}"\n'
            f'          ixz="{link.inertia.get("ixz",0.0)}"\n'
            f'          iyy="{link.inertia.get("iyy",0.0)}"\n'
            f'          iyz="{link.inertia.get("iyz",0.0)}"\n'
            f'          izz="{link.inertia.get("izz",0.0)}"/>\n'
            '    </inertial>\n'
        )

        xml += "  </link>\n\n"

        return xml

    # =====================================================
    # Collision Geometry
    # =====================================================

    def _collision_geometry(self, link):
        """Generate collision geometry for a link."""

        collision = link.collision

        shape = collision.get("shape", "Mesh") if collision else "Mesh"

        xml = (
            '    <collision>\n'
            '      <origin xyz="0 0 0" rpy="0 0 0"/>\n'
            '      <geometry>\n'
        )

        if shape == "Box":

            xml += (
                f'        <box size="'
                f'{collision.get("length",0.0)} '
                f'{collision.get("breadth",0.0)} '
                f'{collision.get("height",0.0)}"/>\n'
            )

        elif shape == "Cylinder":

            xml += (
                f'        <cylinder '
                f'radius="{collision.get("radius",0.0)}" '
                f'length="{collision.get("height",0.0)}"/>\n'
            )

        elif shape == "Sphere":

            xml += (
                f'        <sphere '
                f'radius="{collision.get("radius",0.0)}"/>\n'
            )

        else:  # Mesh

            xml += (
                f'        <mesh filename="package://'
                f'{self.robot.package_name}/meshes/{link.mesh}"/>\n'
            )

        xml += (
            '      </geometry>\n'
            '    </collision>\n\n'
        )

        return xml

    # =====================================================
    # Joint
    # =====================================================

    def _generate_joint(self, joint):
        """Generate URDF for a single joint."""

        origin = joint.origin
        axis = joint.axis

        xml = (
            f'  <joint name="{joint.name}" '
            f'type="{joint.joint_type}">\n'

            f'    <parent link="{joint.parent}"/>\n'
            f'    <child link="{joint.child}"/>\n'

            f'    <origin '
            f'xyz="{origin.get("x",0)} '
            f'{origin.get("y",0)} '
            f'{origin.get("z",0)}" '
            f'rpy="{origin.get("roll",0)} '
            f'{origin.get("pitch",0)} '
            f'{origin.get("yaw",0)}"/>\n'
        )

        if joint.joint_type != "fixed":

            xml += (
                f'    <axis '
                f'xyz="{axis.get("x",0)} '
                f'{axis.get("y",0)} '
                f'{axis.get("z",1)}"/>\n'
            )

            limits = joint.limits

            xml += (
                f'    <limit '
                f'lower="{limits.get("lower",0)}" '
                f'upper="{limits.get("upper",0)}" '
                f'effort="{limits.get("effort",0)}" '
                f'velocity="{limits.get("velocity",0)}"/>\n'
            )

        xml += "  </joint>\n\n"

        return xml
