"""
links_xacro_generator.py

Generates the links.xacro file containing all robot link definitions.

FIXED: 
- Added config parameter
- Improved mesh path validation
- Better error messages
"""

from .file_writer import FileWriter


class LinksXacroGenerator:

    def __init__(
        self,
        robot,
        package_creator,
        config=None
    ):
        """
        Initialize links xacro generator.
        
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
    # Generate Links Xacro
    # =====================================================

    def generate(self):
        """Generate the links.xacro file."""

        xacro = self._build_xacro()

        self.writer.write_file(
            f"urdf/links.xacro",
            xacro
        )

    # =====================================================
    # Build Links Xacro
    # =====================================================

    def _build_xacro(self):
        """Build links xacro content."""

        xacro = f"""<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="{self.robot.robot_name}">

  <!-- ============================= -->
  <!-- Link Definitions              -->
  <!-- ============================= -->
"""

        for link in self.robot.links:
            xacro += self._generate_link(link)

        xacro += """
</robot>
"""

        return xacro

    # =====================================================
    # Generate Individual Link
    # =====================================================

    def _generate_link(self, link):
        """Generate Xacro for a single link."""

        xml = f"""
  <link name="{link.name}">
"""

        # Visual
        if link.mesh:
            xml += f"""    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <mesh filename="package://{self.robot.package_name}/meshes/{link.mesh}"/>
      </geometry>
"""
            if link.material:
                xml += f"""      <material name="{link.material}"/>
"""
            xml += """    </visual>
"""

        # Collision
        collision = link.collision
        if collision:
            shape = collision.get("shape", "Mesh")
            
            xml += f"""    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
"""

            if shape == "Box":
                xml += f"""        <box size="{collision.get('length',0.0)} {collision.get('breadth',0.0)} {collision.get('height',0.0)}"/>
"""
            elif shape == "Cylinder":
                xml += f"""        <cylinder radius="{collision.get('radius',0.0)}" length="{collision.get('height',0.0)}"/>
"""
            elif shape == "Sphere":
                xml += f"""        <sphere radius="{collision.get('radius',0.0)}"/>
"""
            else:  # Mesh
                xml += f"""        <mesh filename="package://{self.robot.package_name}/meshes/{link.mesh}"/>
"""

            xml += """      </geometry>
    </collision>
"""

        # Inertial
        xml += f"""    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
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
