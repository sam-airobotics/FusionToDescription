"""
materials_xacro_generator.py
"""

from .file_writer import FileWriter


class MaterialsXacroGenerator:

    def __init__(self, robot, package_creator):

        self.robot = robot
        self.package = package_creator

        self.writer = FileWriter(
            self.package.package_directory()
        )

    def generate(self):

        self.writer.write_file(
            "urdf/materials.xacro",
            self._build()
        )

    def _build(self):

        return """<?xml version="1.0"?>

<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

  <material name="Grey">
    <color rgba="0.7 0.7 0.7 1"/>
  </material>

  <material name="Black">
    <color rgba="0.1 0.1 0.1 1"/>
  </material>

  <material name="White">
    <color rgba="1 1 1 1"/>
  </material>

  <material name="Blue">
    <color rgba="0.2 0.4 1.0 1"/>
  </material>

  <material name="Red">
    <color rgba="1 0 0 1"/>
  </material>

</robot>
"""