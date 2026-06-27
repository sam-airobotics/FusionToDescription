"""
robot_model.py

Creates a complete RobotModel by collecting information from
all Fusion parsing modules.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from .component_parser import ComponentParser
from .joint_parser import JointParser
from .transform_parser import TransformParser
from .collision_detector import CollisionDetector
from .mass_extractor import MassExtractor
from .inertia_calculator import InertiaCalculator
from .material_parser import MaterialParser
from .mesh_exporter import MeshExporter


# ==========================================================
# Link
# ==========================================================

@dataclass
class Link:

    name: str

    mesh: str = ""

    material: str = "Default"

    mass: float = 0.0

    center_of_mass: tuple = (
        0.0,
        0.0,
        0.0
    )

    origin: dict = field(
        default_factory=dict
    )

    collision: dict = field(
        default_factory=dict
    )

    inertia: dict = field(
        default_factory=dict
    )


# ==========================================================
# Joint
# ==========================================================

@dataclass
class Joint:

    name: str

    joint_type: str

    parent: str

    child: str

    origin: dict = field(
        default_factory=dict
    )

    axis: dict = field(
        default_factory=dict
    )

    limits: dict = field(
        default_factory=dict
    )


# ==========================================================
# Robot Model
# ==========================================================

@dataclass
class RobotModel:

    robot_name: str

    package_name: str

    ros_distro: str

    gazebo_version: str

    links: List[Link] = field(
        default_factory=list
    )

    joints: List[Joint] = field(
        default_factory=list
    )

    metadata: dict = field(
        default_factory=dict
    )

    # ------------------------------------------------------
    # Helpers
    # ------------------------------------------------------

    def get_link(self, name: str) -> Optional[Link]:

        for link in self.links:

            if link.name == name:

                return link

        return None

    def get_joint(self, name: str) -> Optional[Joint]:

        for joint in self.joints:

            if joint.name == name:

                return joint

        return None


# ==========================================================
# Robot Model Builder
# ==========================================================

class RobotModelBuilder:

    def __init__(self, config):

        self.config = config

        self.robot = RobotModel(

            robot_name=config.robot_name,

            package_name=config.package_name,

            ros_distro=config.ros_distro,

            gazebo_version=config.gazebo_version

        )

        self.export_directory = config.mesh_directory()

    # ------------------------------------------------------
    # Build Robot
    # ------------------------------------------------------

    def build(self):

        # ----------------------------------------------
        # Components
        # ----------------------------------------------

        component_parser = ComponentParser()

        self.robot.links = component_parser.parse()

        # ----------------------------------------------
        # Joints
        # ----------------------------------------------

        joint_parser = JointParser()

        self.robot.joints = joint_parser.parse()

        # ----------------------------------------------
        # Transforms
        # ----------------------------------------------

        transform_parser = TransformParser()

        transform_parser.update(self.robot)

        # ----------------------------------------------
        # Collision
        # ----------------------------------------------

        collision = CollisionDetector()

        collision.update(self.robot)

        # ----------------------------------------------
        # Mass Properties
        # ----------------------------------------------

        mass = MassExtractor()

        mass.update(self.robot)

        # ----------------------------------------------
        # Inertia
        # ----------------------------------------------

        inertia = InertiaCalculator()

        inertia.update(self.robot)

        # ----------------------------------------------
        # Materials
        # ----------------------------------------------

        materials = MaterialParser()

        materials.update(self.robot)

        # ----------------------------------------------
        # Mesh Export
        # ----------------------------------------------

        mesh = MeshExporter(

            self.export_directory

        )

        mesh.update(self.robot)

        return self.robot