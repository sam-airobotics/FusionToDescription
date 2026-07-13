import unittest

from fusion.origin_utils import compute_joint_origin


class JointOriginUtilsTests(unittest.TestCase):

    def test_computes_translation_in_parent_frame(self):
        parent_transform = {
            "translation": {"x": 0.0, "y": 0.0, "z": 0.0},
            "rotation": {
                "r11": 1.0, "r12": 0.0, "r13": 0.0,
                "r21": 0.0, "r22": 1.0, "r23": 0.0,
                "r31": 0.0, "r32": 0.0, "r33": 1.0,
            },
        }
        child_transform = {
            "translation": {"x": 0.3, "y": -0.1, "z": 0.5},
            "rotation": {
                "r11": 1.0, "r12": 0.0, "r13": 0.0,
                "r21": 0.0, "r22": 1.0, "r23": 0.0,
                "r31": 0.0, "r32": 0.0, "r33": 1.0,
            },
        }

        origin = compute_joint_origin(parent_transform, child_transform)

        self.assertAlmostEqual(origin["x"], 0.3)
        self.assertAlmostEqual(origin["y"], -0.1)
        self.assertAlmostEqual(origin["z"], 0.5)
        self.assertAlmostEqual(origin["roll"], 0.0)
        self.assertAlmostEqual(origin["pitch"], 0.0)
        self.assertAlmostEqual(origin["yaw"], 0.0)

    def test_falls_back_to_joint_geometry_origin(self):
        fallback = {"x": 1.0, "y": 2.0, "z": 3.0}

        origin = compute_joint_origin(None, None, fallback_origin=fallback)

        self.assertEqual(origin["x"], 1.0)
        self.assertEqual(origin["y"], 2.0)
        self.assertEqual(origin["z"], 3.0)


if __name__ == "__main__":
    unittest.main()
