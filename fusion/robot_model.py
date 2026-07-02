"""
robot_model.py

Creates a complete RobotModel by collecting information from
all Fusion parsing modules.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from .component_parser import get_component_data
from .joint_parser import JointParser
from .transform_parser import TransformParser
from .collision_detector import detect_collision_shape
from .mass_extractor import get_mass_data
from .inertia_calculator import calculate_inertia
from .material_parser import MaterialParser
from .mesh_exporter import MeshExporter
from .joint_tree import orient_joints


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
        # Components (name, mesh filename, collision shape)
        # ----------------------------------------------

        component_data = get_component_data()

        self.robot.links = [
            Link(
                name=item["name"],
                mesh=item["mesh"],
                collision=item["collision"]
            )
            for item in component_data
        ]

        # ----------------------------------------------
        # Joints
        # ----------------------------------------------

        joint_parser = JointParser()

        joint_dicts = joint_parser.parse()

        self.robot.joints = [
            Joint(
                name=j["name"],
                joint_type=j["type"],
                parent=j["parent"],
                child=j["child"],
                origin=j["origin"],
                axis=j["axis"]
            )
            for j in joint_dicts
        ]

        # Fusion joint endpoints have no parent/child semantics.  URDF joints
        # must form a directed tree, so orient the graph from base_link before
        # validation and generation.
        orient_joints(self.robot.joints)

        # ----------------------------------------------
        # Transforms
        # ----------------------------------------------

        transform_parser = TransformParser()

        transforms = transform_parser.parse()

        for link in self.robot.links:

            if link.name in transforms:

                link.origin = transforms[link.name]

        # ----------------------------------------------
        # Mass Properties
        # ----------------------------------------------

        mass_data = get_mass_data()

        mass_by_name = {
            item["name"]: item["mass"]
            for item in mass_data
        }

        for link in self.robot.links:

            link.mass = mass_by_name.get(link.name, 0.0)

        # ----------------------------------------------
        # Inertia
        # ----------------------------------------------

        for link in self.robot.links:

            shape = link.collision.get("shape", "Box")

            try:

                link.inertia = calculate_inertia(
                    shape,
                    link.mass,
                    link.collision
                )

            except Exception:

                link.inertia = {
                    "ixx": 0.0,
                    "iyy": 0.0,
                    "izz": 0.0
                }

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

        mesh.export_all()

        return self.robot
