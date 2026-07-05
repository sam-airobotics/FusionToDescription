"""
links_xacro_generator.py

Generates the links.xacro file containing all robot link
definitions.
"""

from .file_writer import FileWriter


class LinksXacroGenerator:

    def __init__(
        self,
        robot,
        package_creator,
        config=None
    ):

        self.robot = robot
        self.package = package_creator
        self.config = config

        self.writer = FileWriter(
            self.package.package_directory()
        )

    # =====================================================
    # Generate
    # =====================================================

    def generate(self):

        self.writer.write_file(
            "urdf/links.xacro",
            self._build_xacro()
        )

    # =====================================================
    # Build
    # =====================================================

    def _build_xacro(self):

        xacro = f"""<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro"
       name="{self.robot.robot_name}">

    <!-- ============================================== -->
    <!-- Link Definitions                               -->
    <!-- ============================================== -->
"""

        for link in self.robot.links:

            xacro += self._generate_link(link)

        xacro += """
</robot>
"""

        return xacro

    # =====================================================
    # Link
    # =====================================================

    def _generate_link(self, link):

        xml = f"""
    <link name="{link.name}">
"""

        # -------------------------------------------------
        # Visual
        # -------------------------------------------------

        if link.mesh:

            xml += f"""
        <visual>


            <origin
                xyz="{link.origin['x']} {link.origin['y']} {link.origin['z']}"
                rpy="{link.origin['roll']} {link.origin['pitch']} {link.origin['yaw']}"/>

...

            <geometry>

                <mesh filename="package://{self.robot.package_name}/meshes/{link.mesh}"/>

            </geometry>
"""

            # Material
            if link.material:

                xml += f"""
            <material name="{link.material.name}"/>
"""

            xml += """
        </visual>
"""

        # -------------------------------------------------
        # Collision
        # -------------------------------------------------

        collision = link.collision

        if collision:

            shape = collision.get(
                "shape",
                "Mesh"
            )

            xml += """
        <collision>

            <origin
                xyz="{link.origin['x']} {link.origin['y']} {link.origin['z']}"
                rpy="{link.origin['roll']} {link.origin['pitch']} {link.origin['yaw']}"/>

            <geometry>
"""

            if shape == "Box":

                xml += f"""
                <box size="{collision.get('length',0.0)} {collision.get('breadth',0.0)} {collision.get('height',0.0)}"/>
"""

            elif shape == "Cylinder":

                xml += f"""
                <cylinder
                    radius="{collision.get('radius',0.0)}"
                    length="{collision.get('height',0.0)}"/>
"""

            elif shape == "Sphere":

                xml += f"""
                <sphere
                    radius="{collision.get('radius',0.0)}"/>
"""

            else:

                xml += f"""
                <mesh filename="package://{self.robot.package_name}/meshes/{link.mesh}"/>
"""

            xml += """
            </geometry>

        </collision>
"""

        # -------------------------------------------------
        # Inertial
        # -------------------------------------------------

        xml += f"""
        <inertial>

            <origin
        xyz="{link.center_of_mass[0]} {link.center_of_mass[1]} {link.center_of_mass[2]}"
        rpy="0 0 0"/>

            <mass value="{link.mass}"/>

            <inertia

                ixx="{link.inertia.get('ixx',0.0)}"
                ixy="{link.inertia.get('ixy',0.0)}"
                ixz="{link.inertia.get('ixz',0.0)}"

                iyy="{link.inertia.get('iyy',0.0)}"
                iyz="{link.inertia.get('iyz',0.0)}"

                izz="{link.inertia.get('izz',0.0)}"/>

        </inertial>

    </link>
"""

        return xml