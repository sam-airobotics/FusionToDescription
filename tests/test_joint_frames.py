import unittest

from fusion.origin_utils import compute_relative_pose, transform_vector_to_frame


def frame(x=0.0, y=0.0, z=0.0, rotation=None):
    return {
        "translation": {"x": x, "y": y, "z": z},
        "rotation": rotation or {
            "r11": 1.0, "r12": 0.0, "r13": 0.0,
            "r21": 0.0, "r22": 1.0, "r23": 0.0,
            "r31": 0.0, "r32": 0.0, "r33": 1.0,
        },
    }


class JointFrameMathTests(unittest.TestCase):

    def test_joint_and_child_frames_do_not_duplicate_assembly_translation(self):
        parent = frame()
        joint = frame(x=20.0, y=0.0, z=0.0)
        child = frame(x=20.0, y=0.0, z=0.0)

        joint_origin = compute_relative_pose(parent, joint)
        child_origin = compute_relative_pose(joint, child)

        self.assertAlmostEqual(joint_origin["x"], 0.2)
        self.assertAlmostEqual(child_origin["x"], 0.0)

    def test_child_mesh_offset_is_relative_to_joint_not_world(self):
        joint = frame(x=20.0, y=10.0, z=0.0)
        child = frame(x=25.0, y=10.0, z=0.0)

        offset = compute_relative_pose(joint, child)

        self.assertAlmostEqual(offset["x"], 0.05)
        self.assertAlmostEqual(offset["y"], 0.0)
        self.assertAlmostEqual(offset["z"], 0.0)

    def test_vector_is_expressed_in_joint_frame(self):
        ninety_z = {
            "r11": 0.0, "r12": -1.0, "r13": 0.0,
            "r21": 1.0, "r22": 0.0, "r23": 0.0,
            "r31": 0.0, "r32": 0.0, "r33": 1.0,
        }
        joint = frame(rotation=ninety_z)

        local = transform_vector_to_frame(
            joint,
            {"x": 1.0, "y": 0.0, "z": 0.0},
        )

        self.assertAlmostEqual(local["x"], 0.0)
        self.assertAlmostEqual(local["y"], -1.0)
        self.assertAlmostEqual(local["z"], 0.0)


if __name__ == "__main__":
    unittest.main()
