import unittest

from fusion.joint_tree import orient_joints


class JointMotionOrientationTests(unittest.TestCase):

    def test_reversing_joint_inverts_axis_and_limits(self):
        joints = [
            {
                "name": "wheel_joint",
                "type": "revolute",
                "parent": "wheel",
                "child": "base_link",
                "_parent_frame": "W",
                "_child_frame": "B",
                "_joint_frame": "J",
                "_axis_world": {"x": 0.0, "y": 0.0, "z": 1.0},
                "limits": {
                    "lower": -1.0,
                    "upper": 2.0,
                    "effort": 10.0,
                    "velocity": 3.0,
                },
            }
        ]

        orient_joints(joints)

        joint = joints[0]
        self.assertEqual(joint["parent"], "base_link")
        self.assertEqual(joint["child"], "wheel")
        self.assertEqual(joint["_parent_frame"], "B")
        self.assertEqual(joint["_child_frame"], "W")
        self.assertEqual(joint["_axis_world"], {"x": 0.0, "y": 0.0, "z": -1.0})
        self.assertEqual(joint["limits"]["lower"], -2.0)
        self.assertEqual(joint["limits"]["upper"], 1.0)


if __name__ == "__main__":
    unittest.main()
