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

        return f"""cmake_minimum_required(VERSION 3.8)
project({package})

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()

install(
  DIRECTORY config launch urdf meshes rviz worlds
  DESTINATION share/${{PROJECT_NAME}}
)
"""
