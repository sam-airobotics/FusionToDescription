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

        # Prevent duplicate material definitions
        exported = set()

        for link in self.robot.links:

            material = link.material

            if material is None:
                continue

            if material.name in exported:
                continue

            exported.add(material.name)

            color = material.color

            rgba = (
                f"{color.r:.6f} "
                f"{color.g:.6f} "
                f"{color.b:.6f} "
                f"{color.a:.6f}"
            )

            xacro += f"""
    <material name={quoteattr(material.name)}>
        <color rgba="{rgba}"/>
    </material>
"""

        xacro += """
</robot>
"""

        return xacro