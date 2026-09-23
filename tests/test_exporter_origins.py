"""Regression tests for the normalized URDF frame contract."""
import unittest
from types import SimpleNamespace
from exporter.urdf_generator import URDFGenerator

class LinkFrameTests(unittest.TestCase):
    def test_visual_and_collision_origins_ignore_occurrence_pose(self):
        robot = SimpleNamespace(robot_name="demo", package_name="demo", links=[], joints=[])
        link = SimpleNamespace(
            name="camera", mesh="camera.stl", material=SimpleNamespace(name="Default"),
            mass=1.0, center_of_mass=(0.0, 0.0, 0.0),
            inertia={"ixx": 1.0, "iyy": 1.0, "izz": 1.0},
            origin={"x": 0.075, "y": 0.0, "z": 0.035},
            collision={"shape": "Mesh"},
        )
        xml = URDFGenerator(robot, SimpleNamespace(package_directory=lambda: "."))._generate_link(link)
        self.assertEqual(xml.count('<origin xyz="0 0 0" rpy="0 0 0"/>'), 3)
        self.assertNotIn('0.075 0 0.035', xml)

if __name__ == "__main__":
    unittest.main()
