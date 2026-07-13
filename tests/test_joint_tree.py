import unittest
from dataclasses import dataclass

from fusion.joint_tree import orient_joints


@dataclass
class Joint:
    parent: str
    child: str


class OrientJointsTests(unittest.TestCase):

    def test_orients_star_away_from_base_link(self):
        joints = [
            Joint("front_wheel", "base_link"),
            Joint("rear_wheel", "base_link"),
            Joint("camera_link", "base_link"),
        ]

        orient_joints(joints)

        self.assertEqual(
            [(joint.parent, joint.child) for joint in joints],
            [
                ("base_link", "front_wheel"),
                ("base_link", "rear_wheel"),
                ("base_link", "camera_link"),
            ],
        )

    def test_orients_a_chain_regardless_of_raw_endpoint_order(self):
        joints = [
            {"parent": "arm", "child": "base_link"},
            {"parent": "tool", "child": "arm"},
        ]

        orient_joints(joints)

        self.assertEqual(
            [(joint["parent"], joint["child"]) for joint in joints],
            [("base_link", "arm"), ("arm", "tool")],
        )

    def test_preserves_unique_root_when_base_link_is_absent(self):
        joints = [Joint("chassis", "arm"), Joint("arm", "tool")]

        orient_joints(joints)

        self.assertEqual(
            [(joint.parent, joint.child) for joint in joints],
            [("chassis", "arm"), ("arm", "tool")],
        )


if __name__ == "__main__":
    unittest.main()
