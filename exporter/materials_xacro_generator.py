"""
materials_xacro_generator.py

Generates the materials.xacro file containing visual material definitions.

FIXED: Added config parameter for consistency
"""

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

        xacro = f"""<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="{self.robot.robot_name}">

  <!-- ============================= -->
  <!-- Material Definitions          -->
  <!-- ============================= -->

  <material name="Default">
    <color rgba="0.8 0.8 0.8 1.0"/>
  </material>

  <material name="Silver">
    <color rgba="0.7 0.7 0.7 1.0"/>
  </material>

  <material name="Black">
    <color rgba="0.1 0.1 0.1 1.0"/>
  </material>

  <material name="Red">
    <color rgba="1.0 0.0 0.0 1.0"/>
  </material>

  <material name="Green">
    <color rgba="0.0 1.0 0.0 1.0"/>
  </material>

  <material name="Blue">
    <color rgba="0.0 0.0 1.0 1.0"/>
  </material>

  <material name="Yellow">
    <color rgba="1.0 1.0 0.0 1.0"/>
  </material>

</robot>
"""

        return xacro
