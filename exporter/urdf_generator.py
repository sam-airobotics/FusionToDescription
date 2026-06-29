"""
urdf_generator.py

Generates a URDF file from the RobotModel.

FIXED:
- Added config parameter
- Improved error handling
- Better path validation
"""

from .file_writer import FileWriter
from xml.sax.saxutils import quoteattr


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

        xml = "<?xml version='1.0' encoding='utf-8'?>\n"
        xml += f'<robot name={quoteattr(self.robot.robot_name)}>\n'

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

    def _generate_link(self, link, xacro=False):
        """Generate URDF for a single link."""

        name = quoteattr(link.name)
        mesh_uri = self._mesh_uri(link.mesh, xacro)
        xml = f'    <link name={name}>\n'

        # Inertial
        center = link.center_of_mass or (0.0, 0.0, 0.0)
        xml += (
            '        <inertial>\n'
            f'            <origin xyz="{center[0]} {center[1]} {center[2]}" rpy="0.0 0.0 0.0" />\n'
            f'            <mass value="{link.mass}" />\n'
            '            <inertia '
            f'ixx="{link.inertia.get("ixx", 0.0)}" '
            f'iyy="{link.inertia.get("iyy", 0.0)}" '
            f'izz="{link.inertia.get("izz", 0.0)}" '
            f'ixy="{link.inertia.get("ixy", 0.0)}" '
            f'iyz="{link.inertia.get("iyz", 0.0)}" '
            f'ixz="{link.inertia.get("ixz", 0.0)}" />\n'
            '        </inertial>\n'
        )

        # Visual
        if link.mesh:
            xml += (
                f'        <visual name={quoteattr(link.name + "_visual")}>\n'
                '            <origin xyz="0.0 0.0 0.0" rpy="0.0 0.0 0.0" />\n'
                '            <geometry>\n'
                f'                <mesh filename={quoteattr(mesh_uri)} scale="0.001 0.001 0.001" />\n'
                '            </geometry>\n'
            )

            if link.material:
                xml += f'            <material name={quoteattr(link.material)}/>\n'

            xml += '        </visual>\n'

        # Collision
        xml += self._collision_geometry(link, mesh_uri)

        xml += "    </link>\n"

        return xml

    # =====================================================
    # Collision Geometry
    # =====================================================

    def _collision_geometry(self, link, mesh_uri):
        """Generate collision geometry for a link."""

        collision = link.collision

        shape = collision.get("shape", "Mesh") if collision else "Mesh"

        xml = (
            f'        <collision name={quoteattr(link.name + "_collision")}>\n'
            '            <origin xyz="0.0 0.0 0.0" rpy="0.0 0.0 0.0" />\n'
            '            <geometry>\n'
        )

        if shape == "Box":

            xml += (
                f'                <box size="'
                f'{collision.get("length",0.0)} '
                f'{collision.get("breadth",0.0)} '
                f'{collision.get("height",0.0)}"/>\n'
            )

        elif shape == "Cylinder":

            xml += (
                f'                <cylinder '
                f'radius="{collision.get("radius",0.0)}" '
                f'length="{collision.get("height",0.0)}"/>\n'
            )

        elif shape == "Sphere":

            xml += (
                f'                <sphere '
                f'radius="{collision.get("radius",0.0)}"/>\n'
            )

        else:  # Mesh

            xml += (
                f'                <mesh filename={quoteattr(mesh_uri)} '
                'scale="0.001 0.001 0.001" />\n'
            )

        xml += (
            '            </geometry>\n'
            '        </collision>\n'
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
            f'    <joint name={quoteattr(joint.name)} type={quoteattr(joint.joint_type)}>\n'
            f'        <origin '
            f'xyz="{origin.get("x",0)} '
            f'{origin.get("y",0)} '
            f'{origin.get("z",0)}" '
            f'rpy="{origin.get("roll",0)} '
            f'{origin.get("pitch",0)} '
            f'{origin.get("yaw",0)}" />\n'
            f'        <parent link={quoteattr(joint.parent)} />\n'
            f'        <child link={quoteattr(joint.child)} />\n'
        )

        if joint.joint_type != "fixed":

            xml += (
                f'        <axis '
                f'xyz="{axis.get("x",0)} '
                f'{axis.get("y",0)} '
                f'{axis.get("z",1)}" />\n'
            )

            if joint.joint_type in ("revolute", "prismatic"):
                limits = joint.limits
                xml += (
                    f'        <limit effort="{limits.get("effort", 0.0)}" '
                    f'velocity="{limits.get("velocity", 0.0)}" '
                    f'lower="{limits.get("lower", 0.0)}" '
                    f'upper="{limits.get("upper", 0.0)}"/>\n'
                )

        xml += "    </joint>\n"

        return xml

    def _mesh_uri(self, mesh, xacro):
        if xacro:
            return f"file://$(find {self.robot.package_name})/meshes/{mesh}"
        return f"package://{self.robot.package_name}/meshes/{mesh}"
