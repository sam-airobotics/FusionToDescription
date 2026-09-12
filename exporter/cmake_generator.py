"""Generate CMakeLists.txt for the exported ROS 2 package."""

from .file_writer import FileWriter


class CMakeGenerator:
    def __init__(self, robot, package_creator):
        self.robot = robot
        self.package = package_creator
        self.writer = FileWriter(self.package.package_directory())

    def generate(self):
        return self.writer.write_file("CMakeLists.txt", self._build_cmake())

    def _build_cmake(self):
        package = self.robot.package_name
        return f'''cmake_minimum_required(VERSION 3.8)
project({package})

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY config launch urdf meshes rviz worlds
  DESTINATION share/${{PROJECT_NAME}}
)

ament_package()
'''
