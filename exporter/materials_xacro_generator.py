"""
materials_xacro_generator.py

Generates the materials.xacro file containing visual
material definitions extracted from the RobotModel.
"""

from xml.sax.saxutils import quoteattr

from .file_writer import FileWriter


class MaterialsXacroGenerator:

    def __init__(
        self,
        robot,
        package_creator,
        config=None
    ):
        """
        Initialize materials xacro generator.
        """

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
            "urdf/materials.xacro",
            self._build_xacro()
        )

    # =====================================================
    # Build
    # =====================================================

    def _build_xacro(self):

        xacro = """<?xml version="1.0"?>

<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

    <!-- ================================================= -->
    <!-- Material Definitions                              -->
    <!-- ================================================= -->
"""

        exported = set()

        for link in self.robot.links:

            material = link.material

            if material is None:
                continue

            if not material.name:
                continue

            if material.name in exported:
                continue

            exported.add(material.name)

            color = material.color

            if color is None:
                r = g = b = 0.7
                a = 1.0
            else:
                r = color.r
                g = color.g
                b = color.b
                a = color.a

            xacro += f"""
    <material name={quoteattr(material.name)}>
        <color rgba="{r:.6f} {g:.6f} {b:.6f} {a:.6f}"/>
    </material>
"""

        xacro += """
</robot>
"""

        return xacro
