"""
gazebo_plugin_xacro_generator.py

Generates Gazebo Harmonic plugin definitions.
"""

from .file_writer import FileWriter


class GazeboPluginXacroGenerator:

    def __init__(self, robot, package_creator):

        self.robot = robot
        self.package = package_creator

        self.writer = FileWriter(
            self.package.package_directory()
        )

    def generate(self):

        self.writer.write_file(
            "urdf/gazebo_plugins.xacro",
            self._build()
        )

    def _build(self):

        return """<?xml version="1.0"?>

<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Gazebo Harmonic plugins -->

  <!-- Plugins will be generated here -->

</robot>
"""