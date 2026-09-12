"""Generate materials.xacro with extracted appearance colors."""

from xml.sax.saxutils import quoteattr

from .file_writer import FileWriter


class MaterialsXacroGenerator:
    def __init__(self, robot, package_creator, config=None):
        self.robot = robot
        self.package = package_creator
        self.config = config
        self.writer = FileWriter(self.package.package_directory())

    def generate(self):
        return self.writer.write_file("urdf/materials.xacro", self._build_xacro())

    def _build_xacro(self):
        xacro = '<?xml version="1.0"?>\n<robot xmlns:xacro="http://www.ros.org/wiki/xacro">\n'
        exported = set()
        for link in self.robot.links:
            material = link.material
            if material is None or not material.name or material.name in exported:
                continue
            exported.add(material.name)
            color = material.color
            r, g, b, a = color.r, color.g, color.b, color.a
            xacro += (
                f'  <material name={quoteattr(material.name)}>\n'
                f'    <color rgba="{r:.6f} {g:.6f} {b:.6f} {a:.6f}"/>\n'
                '  </material>\n'
            )
        return xacro + '</robot>\n'
