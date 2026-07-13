import unittest
from types import SimpleNamespace

from utils.validate import Validator


def link(name):
    return SimpleNamespace(name=name, mass=1.0, mesh=f"{name}.stl")


def joint(name, parent, child):
    return SimpleNamespace(name=name, parent=parent, child=child)


class JointTreeValidationTests(unittest.TestCase):

    def validator_for(self, links, joints):
        robot = SimpleNamespace(links=links, joints=joints)
        return Validator(SimpleNamespace(), robot)

    def test_rejects_multiple_roots_from_reversed_star(self):
        validator = self.validator_for(
            [link("base_link"), link("left_wheel"), link("right_wheel")],
            [
                joint("left_joint", "left_wheel", "base_link"),
                joint("right_joint", "right_wheel", "base_link"),
            ],
        )

        validator._validate_joints()

        self.assertTrue(any("multiple parent joints" in error for error in validator.errors))
        self.assertTrue(any("found 2 root links" in error for error in validator.errors))

    def test_accepts_a_single_connected_tree(self):
        validator = self.validator_for(
            [link("base_link"), link("left_wheel"), link("right_wheel")],
            [
                joint("left_joint", "base_link", "left_wheel"),
                joint("right_joint", "base_link", "right_wheel"),
            ],
        )

        validator._validate_joints()

        self.assertEqual(validator.errors, [])


if __name__ == "__main__":
    unittest.main()
