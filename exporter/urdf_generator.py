"""
urdf_generator.py

Generates a URDF file from the RobotModel.
"""

from .file_writer import FileWriter
from xml.sax.saxutils import quoteattr


class URDFGenerator:
    """Render the RobotModel as valid URDF/XML."""

    def __init__(self, robot, package_creator, config=None):
        self.robot = robot
        self.package = package_creator
        self.config = config
        self.writer = FileWriter(self.package.package_directory())

    def generate(self):
        urdf = self._build_urdf()
        return self.writer.write_file(
            f"urdf/{self.robot.robot_name}.urdf",
            urdf,
        )

    def _build_urdf(self):
        xml = "<?xml version='1.0' encoding='utf-8'?>\n"
        xml += f'<robot name={quoteattr(self.robot.robot_name)}>\n'
        for link in self.robot.links:
            xml += self._generate_link(link)
        for joint in self.robot.joints:
            xml += self._generate_joint(joint)
        xml += "</robot>\n"
        return xml

    @staticmethod
    def _origin_xyz(origin):
        if not origin:
            return "0.0 0.0 0.0"
        if "translation" in origin:
            t = origin.get("translation", {})
            return f"{t.get('x', 0.0)} {t.get('y', 0.0)} {t.get('z', 0.0)}"
        return f"{origin.get('x', 0.0)} {origin.get('y', 0.0)} {origin.get('z', 0.0)}"

    @staticmethod
    def _origin_rpy(origin):
        if not origin or "translation" in origin:
            return "0.0 0.0 0.0"
        return f"{origin.get('roll', 0.0)} {origin.get('pitch', 0.0)} {origin.get('yaw', 0.0)}"

    def _generate_link(self, link, xacro=False):
        name = quoteattr(link.name)
        mesh_uri = self._mesh_uri(link.mesh)
        xml = f'    <link name={name}>\n'
        center = link.center_of_mass or (0.0, 0.0, 0.0)
        xml += (
            "        <inertial>\n"
            f'            <origin xyz="{center[0]} {center[1]} {center[2]}" rpy="0.0 0.0 0.0"/>\n'
            f'            <mass value="{link.mass}"/>\n'
            "            <inertia "
            f'ixx="{link.inertia.get("ixx", 0.0)}" '
            f'iyy="{link.inertia.get("iyy", 0.0)}" '
            f'izz="{link.inertia.get("izz", 0.0)}" '
            f'ixy="{link.inertia.get("ixy", 0.0)}" '
            f'iyz="{link.inertia.get("iyz", 0.0)}" '
            f'ixz="{link.inertia.get("ixz", 0.0)}"/>\n'
            "        </inertial>\n"
        )
        if link.mesh:
            origin_xyz = self._origin_xyz(link.origin)
            xml += (
                f'        <visual name={quoteattr(link.name + "_visual")}>\n'
                f'            <origin xyz="{origin_xyz}" rpy="0.0 0.0 0.0"/>\n'
                "            <geometry>\n"
                f'                <mesh filename={quoteattr(mesh_uri)} scale="0.001 0.001 0.001"/>\n'
                "            </geometry>\n"
            )
            material_name = getattr(link.material, "name", None)
            if material_name:
                xml += f'            <material name={quoteattr(material_name)}/>\n'
            xml += "        </visual>\n"
        xml += self._collision_geometry(link, mesh_uri)
        xml += "    </link>\n"
        return xml

    def _collision_geometry(self, link, mesh_uri):
        collision = link.collision or {}
        shape = collision.get("shape", "Mesh")
        origin_xyz = self._origin_xyz(link.origin)
        xml = (
            f'        <collision name={quoteattr(link.name + "_collision")}>\n'
            f'            <origin xyz="{origin_xyz}" rpy="0.0 0.0 0.0"/>\n'
            "            <geometry>\n"
        )
        if shape == "Box":
            xml += f'                <box size="{collision.get("length", 0.0)} {collision.get("breadth", 0.0)} {collision.get("height", 0.0)}"/>\n'
        elif shape == "Cylinder":
            xml += f'                <cylinder radius="{collision.get("radius", 0.0)}" length="{collision.get("height", 0.0)}"/>\n'
        elif shape == "Sphere":
            xml += f'                <sphere radius="{collision.get("radius", 0.0)}"/>\n'
        else:
            xml += f'                <mesh filename={quoteattr(mesh_uri)} scale="0.001 0.001 0.001"/>\n'
        return xml + "            </geometry>\n        </collision>\n"

    def _generate_joint(self, joint):
        origin = joint.origin or {}
        axis = joint.axis or {}
        xml = (
            f'    <joint name={quoteattr(joint.name)} type={quoteattr(joint.joint_type)}>\n'
            f'        <origin xyz="{self._origin_xyz(origin)}" rpy="{self._origin_rpy(origin)}"/>\n'
            f'        <parent link={quoteattr(joint.parent)}/>\n'
            f'        <child link={quoteattr(joint.child)}/>\n'
        )
        if joint.joint_type != "fixed":
            xml += f'        <axis xyz="{axis.get("x", 0.0)} {axis.get("y", 0.0)} {axis.get("z", 1.0)}"/>\n'
            if joint.joint_type in ("revolute", "prismatic"):
                limits = joint.limits or {}
                # URDF requires effort/velocity on a limit element. Upstream ACDC4Robot
                # uses large defaults when Fusion does not provide actuator limits.
                xml += (
                    f'        <limit lower="{limits.get("lower", 0.0)}" '
                    f'upper="{limits.get("upper", 0.0)}" '
                    f'effort="{limits.get("effort", 1_000_000.0)}" '
                    f'velocity="{limits.get("velocity", 1_000_000.0)}"/>\n'
                )
        return xml + "    </joint>\n"

    def _mesh_uri(self, mesh):
        return f"package://{self.robot.package_name}/meshes/{mesh}"
