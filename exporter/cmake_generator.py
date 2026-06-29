"""
cmake_generator.py

Generates the CMakeLists.txt file for a ROS 2
robot description package.
"""

from .file_writer import FileWriter


class CMakeGenerator:

    def __init__(
        self,
        robot,
        package_creator
    ):

        self.robot = robot
        self.package = package_creator

        self.writer = FileWriter(
            self.package.package_directory()
        )

    # =====================================================
    # Generate CMakeLists.txt
    # =====================================================

    def generate(self):

        cmake = self._build_cmake()

        self.writer.write_file(
            "CMakeLists.txt",
            cmake
        )

    # =====================================================
    # Build CMakeLists
    # =====================================================

    def _build_cmake(self):

        package = self.robot.package_name

        return f"""
                    cmake_minimum_required(VERSION 3.8)

                    project({package})

                    find_package(ament_cmake REQUIRED)
                    
                    install(
                        DIRECTORY
                            config
                            launch
                            meshes
                            rviz
                            urdf
                            worlds
                        DESTINATION
                            share/${{PROJECT_NAME}}
                    )

                    ament_package()
                    """
