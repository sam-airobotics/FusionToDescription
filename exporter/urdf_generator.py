"""Generate a URDF from the normalized RobotModel."""

from .file_writer import FileWriter
from xml.sax.saxutils import quoteattr


class URDFGenerator:
    def __init__(self, robot, package_creator, config=None):
        self.robot = robot
        self.package = package_creator
        self.config = config
        self.writer = FileWriter(self.package.package_directory())

    def generate(self):
        return self.writer.write_file(f"urdf/{self.robot.robot_name}.urdf", self._build_urdf())

    @staticmethod
    def _origin_values(origin):
        origin = origin or {}
        if "translation" in origin:
            t = origin.get("translation", {})
            xyz = (t.get("x", 0.0), t.get("y", 0.0), t.get("z", 0.0))
            rpy = (origin.get("roll", 0.0), origin.get("pitch", 0.0), origin.get("yaw", 0.0))
        else:
            xyz = (origin.get("x", 0.0), origin.get("y", 0.0), origin.get("z", 0.0))
            rpy = (origin.get("roll", 0.0), origin.get("pitch", 0.0), origin.get("yaw", 0.0))
        return xyz, rpy

    @classmethod
    def _origin_xml(cls, origin, indent="        "):
        (x, y, z), (r, p, yaw) = cls._origin_values(origin)
        return f'{indent}<origin xyz="{x:.9g} {y:.9g} {z:.9g}" rpy="{r:.9g} {p:.9g} {yaw:.9g}"/>\n'

    def _build_urdf(self):
        xml = f"<?xml version='1.0' encoding='utf-8'?>\n<robot name={quoteattr(self.robot.robot_name)}>\n"
        for link in self.robot.links:
            xml += self._generate_link(link)
        for joint in self.robot.joints:
            xml += self._generate_joint(joint)
        return xml + "</robot>\n"

    def _generate_link(self, link, xacro=False):
        name = quoteattr(link.name)
        xml = f'  <link name={name}>\n'
        center = link.center_of_mass or (0.0, 0.0, 0.0)
        inertia = link.inertia or {}
        xml += "    <inertial>\n"
        xml += f'      <origin xyz="{center[0]:.9g} {center[1]:.9g} {center[2]:.9g}" rpy="0 0 0"/>\n'
        xml += f'      <mass value="{max(float(link.mass), 0.0):.9g}"/>\n'
        xml += (
            f'      <inertia ixx="{max(float(inertia.get("ixx", 1e-9)), 1e-12):.9g}" '
            f'iyy="{max(float(inertia.get("iyy", 1e-9)), 1e-12):.9g}" '
            f'izz="{max(float(inertia.get("izz", 1e-9)), 1e-12):.9g}" '
            f'ixy="{float(inertia.get("ixy", 0.0)):.9g}" '
            f'iyz="{float(inertia.get("iyz", 0.0)):.9g}" '
            f'ixz="{float(inertia.get("ixz", 0.0)):.9g}"/>\n'
        )
        xml += "    </inertial>\n"

        if link.mesh:
            uri = self._mesh_uri(link.mesh)
            xml += f'    <visual name={quoteattr(link.name + "_visual")}>\n'
            xml += self._origin_xml(link.origin, "      ")
            xml += "      <geometry>\n"
            xml += f'        <mesh filename={quoteattr(uri)} scale="0.001 0.001 0.001"/>\n'
            xml += "      </geometry>\n"
            material_name = getattr(link.material, "name", None)
            if material_name:
                xml += f'      <material name={quoteattr(material_name)}/>\n'
            xml += "    </visual>\n"

        xml += self._collision_geometry(link, uri if link.mesh else None)
        return xml + "  </link>\n"

    def _collision_geometry(self, link, mesh_uri=None):
        collision = link.collision or {}
        shape = collision.get("shape", "Mesh")
        xml = f'    <collision name={quoteattr(link.name + "_collision")}>\n'
        xml += self._origin_xml(link.origin, "      ")
        xml += "      <geometry>\n"
        if shape == "Box":
            xml += (
                f'        <box size="{float(collision.get("length", 0.001)):.9g} '
                f'{float(collision.get("breadth", 0.001)):.9g} '
                f'{float(collision.get("height", 0.001)):.9g}"/>\n'
            )
        elif shape == "Cylinder":
            xml += f'        <cylinder radius="{float(collision.get("radius", 0.0005)):.9g}" length="{float(collision.get("height", 0.001)):.9g}"/>\n'
        elif shape == "Sphere":
            xml += f'        <sphere radius="{float(collision.get("radius", 0.0005)):.9g}"/>\n'
        elif mesh_uri:
            xml += f'        <mesh filename={quoteattr(mesh_uri)} scale="0.001 0.001 0.001"/>\n'
        else:
            xml += '        <box size="0.001 0.001 0.001"/>\n'
        return xml + "      </geometry>\n    </collision>\n"

    def _generate_joint(self, joint):
        origin = joint.origin or {}
        axis = joint.axis or {}
        xml = f'  <joint name={quoteattr(joint.name)} type={quoteattr(joint.joint_type)}>\n'
        xml += self._origin_xml(origin, "    ")
        xml += f'    <parent link={quoteattr(joint.parent)}/>\n'
        xml += f'    <child link={quoteattr(joint.child)}/>\n'
        if joint.joint_type != "fixed":
            xml += f'    <axis xyz="{float(axis.get("x", 0.0)):.9g} {float(axis.get("y", 0.0)):.9g} {float(axis.get("z", 1.0)):.9g}"/>\n'
            if joint.joint_type in ("revolute", "prismatic") and joint.limits:
                limits = joint.limits
                xml += (
                    f'    <limit lower="{float(limits["lower"]):.9g}" upper="{float(limits["upper"]):.9g}" '
                    f'effort="{max(float(limits.get("effort", 1.0)), 1e-9):.9g}" '
                    f'velocity="{max(float(limits.get("velocity", 1.0)), 1e-9):.9g}"/>\n'
                )
        return xml + "  </joint>\n"

    def _mesh_uri(self, mesh):
        return f"package://{self.robot.package_name}/meshes/{mesh}"
