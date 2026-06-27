"""
links_xacro_generator.py

Generates all robot links.
"""

from .file_writer import FileWriter


class LinksXacroGenerator:

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
            "urdf/links.xacro",
            self._build()
        )

    # =====================================================
    # Build File
    # =====================================================

    def _build(self):

        xml = """<?xml version="1.0"?>

<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

"""

        for link in self.robot.links:
            xml += self._generate_link(link)

        xml += "\n</robot>\n"

        return xml

    # =====================================================
    # Single Link
    # =====================================================

    def _generate_link(self, link):

        collision = link.collision
        shape = collision.get("shape", "Mesh")

        xml = f"""  <link name="{link.name}">

    <!-- Visual -->

    <visual>

      <origin xyz="0 0 0" rpy="0 0 0"/>

      <geometry>

        <mesh filename="package://{self.robot.package_name}/meshes/{link.mesh}"/>

      </geometry>

      <material name="{link.material}"/>

    </visual>

"""

        # ----------------------------------------
        # Collision
        # ----------------------------------------

        xml += """    <collision>

      <origin xyz="0 0 0" rpy="0 0 0"/>

      <geometry>

"""

        if shape == "Box":

            xml += (
                f'        <box size="{collision.get("length",0)} '
                f'{collision.get("breadth",0)} '
                f'{collision.get("height",0)}"/>\n'
            )

        elif shape == "Cylinder":

            xml += (
                f'        <cylinder radius="{collision.get("radius",0)}" '
                f'length="{collision.get("height",0)}"/>\n'
            )

        elif shape == "Sphere":

            xml += (
                f'        <sphere radius="{collision.get("radius",0)}"/>\n'
            )

        else:

            xml += (
                f'        <mesh filename="package://{self.robot.package_name}/meshes/{link.mesh}"/>\n'
            )

        xml += """      </geometry>

    </collision>

"""

        # ----------------------------------------
        # Inertial
        # ----------------------------------------

        inertia = link.inertia

        xml += f"""    <inertial>

      <origin xyz="0 0 0" rpy="0 0 0"/>

      <mass value="{link.mass}"/>

      <inertia

          ixx="{inertia.get('ixx',0)}"

          ixy="{inertia.get('ixy',0)}"

          ixz="{inertia.get('ixz',0)}"

          iyy="{inertia.get('iyy',0)}"

          iyz="{inertia.get('iyz',0)}"

          izz="{inertia.get('izz',0)}"/>

    </inertial>

  </link>


"""

        return xml