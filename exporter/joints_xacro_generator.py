"""
joints_xacro_generator.py

Generates all robot joints.
"""

from .file_writer import FileWriter


class JointsXacroGenerator:

    def __init__(self, robot, package_creator):

        self.robot = robot
        self.package = package_creator

        self.writer = FileWriter(
            self.package.package_directory()
        )

    # =====================================================
    # Generate
    # =====================================================

    def generate(self):

        self.writer.write_file(
            "urdf/joints.xacro",
            self._build()
        )

    # =====================================================
    # Build File
    # =====================================================

    def _build(self):

        xml = """<?xml version="1.0"?>

<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

"""

        for joint in self.robot.joints:
            xml += self._generate_joint(joint)

        xml += "\n</robot>\n"

        return xml

    # =====================================================
    # Single Joint
    # =====================================================

    def _generate_joint(self, joint):

        origin = joint.origin
        axis = joint.axis
        limits = joint.limits

        xml = f"""  <joint name="{joint.name}" type="{joint.joint_type}">

    <parent link="{joint.parent}"/>

    <child link="{joint.child}"/>

    <origin

        xyz="{origin.get('x',0)} {origin.get('y',0)} {origin.get('z',0)}"

        rpy="{origin.get('roll',0)} {origin.get('pitch',0)} {origin.get('yaw',0)}"/>

"""

        if joint.joint_type != "fixed":

            xml += f"""    <axis

        xyz="{axis.get('x',0)} {axis.get('y',0)} {axis.get('z',1)}"/>

    <limit

        lower="{limits.get('lower',0)}"

        upper="{limits.get('upper',0)}"

        effort="{limits.get('effort',0)}"

        velocity="{limits.get('velocity',0)}"/>

"""

        xml += """  </joint>


"""

        return xml