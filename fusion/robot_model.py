"""Build the normalized robot model from Fusion 360 data."""

from dataclasses import dataclass, field
from typing import List, Optional

from .component_parser import get_component_data
from .joint_parser import JointParser
from .mass_extractor import get_mass_data
from .inertia_calculator import calculate_inertia
from .material_parser import MaterialParser
from .mesh_exporter import MeshExporter
from .material import Material


@dataclass
class Link:
    name: str
    mesh: str = ""
    material: Material = field(default_factory=Material)
    mass: float = 0.0
    center_of_mass: tuple = (0.0, 0.0, 0.0)
    # Geometry exported for a link is already expressed in that link's CAD
    # frame. The assembly placement belongs exclusively to the connecting
    # joint, so occurrence.transform2 must never be copied here.
    origin: dict = field(default_factory=dict)
    collision: dict = field(default_factory=dict)
    inertia: dict = field(default_factory=dict)
    component_name: str = ""
    occurrence_path: str = ""


@dataclass
class Joint:
    name: str
    joint_type: str
    parent: str
    child: str
    origin: dict = field(default_factory=dict)
    axis: dict = field(default_factory=dict)
    limits: dict = field(default_factory=dict)


@dataclass
class RobotModel:
    robot_name: str
    package_name: str
    ros_distro: str
    gazebo_version: str
    links: List[Link] = field(default_factory=list)
    joints: List[Joint] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def get_link(self, name: str) -> Optional[Link]:
        return next((link for link in self.links if link.name == name), None)

    def get_joint(self, name: str) -> Optional[Joint]:
        return next((joint for joint in self.joints if joint.name == name), None)


class RobotModelBuilder:
    """Build a RobotModel whose geometry/poses are SI-normalized."""

    def __init__(self, config):
        self.config = config
        self.robot = RobotModel(
            robot_name=config.robot_name,
            package_name=config.package_name,
            ros_distro=config.ros_distro,
            gazebo_version=config.gazebo_version,
        )
        self.export_directory = config.mesh_directory()

    def build(self):
        component_data = get_component_data()
        if not component_data:
            raise RuntimeError("No exportable Fusion components were found.")

        self.robot.links = [
            Link(
                name=item["name"],
                mesh=item["mesh"],
                collision=item["collision"],
                component_name=item.get("component_name", item["name"]),
                occurrence_path=item.get("occurrence_path", ""),
            )
            for item in component_data
        ]

        link_names = {link.name for link in self.robot.links}
        # JointParser orients the undirected Fusion joint graph before it
        # calculates each origin/axis, keeping kinematics consistent with the
        # final URDF parent/child direction.
        joint_dicts = JointParser().parse()
        unknown = [
            j for j in joint_dicts
            if j.get("parent") not in link_names or j.get("child") not in link_names
        ]
        if unknown:
            details = ", ".join(
                f'{j.get("name")}: {j.get("parent")} -> {j.get("child")}' for j in unknown
            )
            raise RuntimeError(f"Fusion joints reference links that are not exported: {details}")

        self.robot.joints = [
            Joint(
                name=j["name"],
                joint_type=j["type"],
                parent=j["parent"],
                child=j["child"],
                origin=j["origin"],
                axis=j["axis"],
                limits=j.get("limits", {}),
            )
            for j in joint_dicts
        ]

        # IMPORTANT: do not set link.origin from Occurrence.transform2.
        # The joint origin is the sole assembly-level placement. Reusing
        # occurrence.transform2 as visual/collision origin moves the same
        # component twice in RViz/Gazebo.
        MaterialParser().update(self.robot)

        mass_data = get_mass_data()
        mass_by_name = {item["name"]: item["mass"] for item in mass_data}
        for link in self.robot.links:
            link.mass = max(
                float(mass_by_name.get(
                    link.component_name,
                    mass_by_name.get(link.name, 0.0)
                )),
                1e-6,
            )
            shape = link.collision.get("shape", "Box")
            link.inertia = calculate_inertia(shape, link.mass, link.collision)

        exported_meshes = MeshExporter(self.export_directory).export_all()
        expected = {link.mesh for link in self.robot.links if link.mesh}
        actual = {
            path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
            for path in exported_meshes
        }
        missing = sorted(expected - actual)
        if missing:
            raise RuntimeError("Mesh export incomplete; missing: " + ", ".join(missing))

        return self.robot
