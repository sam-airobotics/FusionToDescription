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

        # origin = link.origin or {}

        # x = origin.get("x", 0.0)
        # y = origin.get("y", 0.0)
        # z = origin.get("z", 0.0)

        # roll = origin.get("roll", 0.0)
        # pitch = origin.get("pitch", 0.0)
        # yaw = origin.get("yaw", 0.0)

        com = link.center_of_mass or (
            0.0,
            0.0,
            0.0
        )

        inertia = link.inertia or {}
        
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
                xyz="0 0 0"
                rpy="0 0 0"/>

...

            <geometry>

                <mesh filename="package://{self.robot.package_name}/meshes/{link.mesh}"/>

            </geometry>
"""

            # Material
            if link.material is not None:

                xml += f"""
            <material name="{link.material.name}"/>
"""

            xml += f"""
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

            xml += f"""
        <collision>

            <origin
                xyz="0 0 0"
                rpy="0 0 0"/>

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

            xml += f"""
            </geometry>

        </collision>
"""

        # -------------------------------------------------
        # Inertial
        # -------------------------------------------------

        xml += f"""
        <inertial>

                <origin
                    xyz="{com[0]} {com[1]} {com[2]}"
                    rpy="0 0 0"/>

            <mass value="{link.mass}"/>

            <inertia

                ixx="{inertia.get('ixx',0.0)}"
                ixy="{inertia.get('ixy',0.0)}"
                ixz="{inertia.get('ixz',0.0)}"

                iyy="{inertia.get('iyy',0.0)}"
                iyz="{inertia.get('iyz',0.0)}"

                izz="{inertia.get('izz',0.0)}"/>

        </inertial>

    </link>
"""

        return xml
