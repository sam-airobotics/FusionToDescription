"""
export_config.py

Stores all export settings used throughout the
FusionToDescription exporter.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ExportConfig:
    """
    Global configuration for an export operation.
    """

    # =====================================================
    # Robot Information
    # =====================================================

    robot_name: str
    export_directory: str

    package_name: str = ""

    # =====================================================
    # Target Platform
    # =====================================================

    ros_distro: str = "jazzy"
    gazebo_version: str = "harmonic"

    # =====================================================
    # Output Formats
    # =====================================================

    generate_xacro: bool = True
    generate_urdf: bool = True
    generate_rviz: bool = True
    generate_gazebo: bool = True
    generate_launch: bool = True
    generate_ros2_control: bool = True

    # =====================================================
    # Collision Settings
    # =====================================================

    collision_type: str = "Primitive"

    primitive_mode: str = "Auto Detect"
    mesh_collision: bool = False

    # =====================================================
    # Mesh Export
    # =====================================================

    mesh_format: str = "stl"

    mesh_quality: str = "high"

    binary_mesh: bool = True

    # =====================================================
    # Export Options
    # =====================================================

    overwrite_existing: bool = True

    export_hidden_components: bool = False

    export_only_visible: bool = True

    # =====================================================
    # Package Information
    # =====================================================

    package_version: str = "0.1.0"

    maintainer_name: str = ""

    maintainer_email: str = ""

    license: str = "Apache-2.0"

    description: str = (
        "Robot description package generated "
        "by FusionToDescription."
    )

    # =====================================================
    # Future Features
    # =====================================================

    enabled_plugins: List[str] = field(
        default_factory=list
    )

    enabled_sensors: List[str] = field(
        default_factory=list
    )

    enabled_controllers: List[str] = field(
        default_factory=list
    )

    # =====================================================
    # Initialization
    # =====================================================

    def __post_init__(self):

        if not self.package_name:

            self.package_name = (
                f"{self.robot_name}_description"
            )

    # =====================================================
    # Helper Methods
    # =====================================================

    def mesh_directory(self):

        return (
            f"{self.export_directory}/"
            f"{self.package_name}/meshes"
        )

    def urdf_directory(self):

        return (
            f"{self.export_directory}/"
            f"{self.package_name}/urdf"
        )

    def launch_directory(self):

        return (
            f"{self.export_directory}/"
            f"{self.package_name}/launch"
        )

    def config_directory(self):

        return (
            f"{self.export_directory}/"
            f"{self.package_name}/config"
        )

    def rviz_directory(self):

        return (
            f"{self.export_directory}/"
            f"{self.package_name}/rviz"
        )

    def worlds_directory(self):

        return (
            f"{self.export_directory}/"
            f"{self.package_name}/worlds"
        )