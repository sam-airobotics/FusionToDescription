"""
materials_xacro_generator.py

Generates the materials.xacro file containing visual material definitions.

FIXED: Added config parameter for consistency
"""

from .file_writer import FileWriter
from xml.sax.saxutils import quoteattr


class MaterialsXacroGenerator:

    def __init__(
        self,
        robot,
        package_creator,
        config=None
    ):
        """
        Initialize materials xacro generator.
        
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
    # Generate Materials Xacro
    # =====================================================

    def generate(self):
        """Generate the materials.xacro file."""

        xacro = self._build_xacro()

        self.writer.write_file(
            f"urdf/materials.xacro",
            xacro
        )

    # =====================================================
    # Build Materials Xacro
    # =====================================================

    def _build_xacro(self):
        """Build materials xacro content."""

        xacro = """<?xml version="1.0"?>

<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

    <!-- ================= COLORS ================= -->
"""

        colors = {
            "Default": "0.8 0.8 0.8 1.0",
            "Silver": "0.7 0.7 0.7 1.0",
            "Black": "0.1 0.1 0.1 1.0",
            "Red": "1.0 0.0 0.0 1.0",
            "Green": "0.0 1.0 0.0 1.0",
            "Blue": "0.0 0.0 1.0 1.0",
            "Yellow": "1.0 1.0 0.0 1.0",
        }
        material_names = {"Default"}
        material_names.update(link.material for link in self.robot.links if link.material)

        for name in sorted(material_names):
            rgba = colors.get(name, colors["Default"])
            xacro += f"""
    <material name={quoteattr(name)}>
        <color rgba="{rgba}"/>
    </material>
"""

        xacro += """
</robot>
"""

        return xacro
