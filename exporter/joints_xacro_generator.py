"""
joints_xacro_generator.py

Generates the optional standalone joints.xacro file.
"""

from .file_writer import FileWriter
from xml.sax.saxutils import quoteattr


class JointsXacroGenerator:
    def __init__(self, robot, package_creator, config=None):
        self.robot = robot
        self.package = package_creator
        self.config = config
        self.writer = FileWriter(self.package.package_directory())

    def generate(self):
        return self.writer.write_file("urdf/joints.xacro", self._build_xacro())

    def _build_xacro(self):
        xacro = (
            '<?xml version="1.0"?>\n'
            '<robot xmlns:xacro="http://www.ros.org/wiki/xacro" '
            f'name={quoteattr(self.robot.robot_name)}>\n\n'
        )
        for joint in self.robot.joints:
            xacro += self._generate_joint(joint)
        return xacro + "</robot>\n"

    @staticmethod
    def _generate_joint(joint):
        origin = joint.origin or {}
        axis = joint.axis or {}
        xml = (
            f'  <joint name={quoteattr(joint.name)} type={quoteattr(joint.joint_type)}>\n'
            f'    <parent link={quoteattr(joint.parent)}/>\n'
            f'    <child link={quoteattr(joint.child)}/>\n'
            f'    <origin xyz="{origin.get("x", 0.0)} {origin.get("y", 0.0)} {origin.get("z", 0.0)}" '
            f'rpy="{origin.get("roll", 0.0)} {origin.get("pitch", 0.0)} {origin.get("yaw", 0.0)}"/>\n'
        )
        if joint.joint_type != "fixed":
            xml += f'    <axis xyz="{axis.get("x", 0.0)} {axis.get("y", 0.0)} {axis.get("z", 1.0)}"/>\n'
            limits = joint.limits or {}
            xml += (
                f'    <limit lower="{limits.get("lower", 0.0)}" upper="{limits.get("upper", 0.0)}" '
                f'effort="{limits.get("effort", 1000000.0)}" velocity="{limits.get("velocity", 1000000.0)}"/>\n'
            )
        return xml + "  </joint>\n\n"
