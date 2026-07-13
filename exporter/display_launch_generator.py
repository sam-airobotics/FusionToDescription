"""
display_launch_generator.py

Generates robot_state_publisher launch file wrapper.

FIXED: Added config parameter for consistency
"""

from .file_writer import FileWriter


class DisplayLaunchGenerator:

    def __init__(
        self,
        robot,
        package_creator,
        config=None
    ):
        """
        Initialize display launch generator.
        
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
    # Generate Display Launch
    # =====================================================

    def generate(self):
        """Generate the robot_state_publisher launch file."""

        launch = self._build_launch()

        self.writer.write_file(
            "launch/robot_state_publisher.launch.py",
            launch
        )

    # =====================================================
    # Build Launch File
    # =====================================================

    def _build_launch(self):
        """Build robot_state_publisher launch file content."""

        package = self.robot.package_name

        launch = f'''"""
Robot State Publisher launch file for {self.robot.robot_name}.
Publishes robot transforms.
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    package_name = "{package}"

    xacro_file = os.path.join(
        get_package_share_directory(package_name),
        "urdf",
        "{self.robot.robot_name}.xacro"
    )

    robot_description = ParameterValue(
        Command(["xacro ", xacro_file]),
        value_type=str
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{{"robot_description": robot_description}}],
        output="screen"
    )

    return LaunchDescription([
        robot_state_publisher
    ])
'''

        return launch
