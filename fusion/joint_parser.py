import traceback
import adsk.core
import adsk.fusion

from .origin_utils import compute_joint_origin


app = adsk.core.Application.get()


class JointParser:

    def __init__(self):

        self.design = app.activeProduct

        if not isinstance(self.design, adsk.fusion.Design):
            raise RuntimeError("No active Fusion Design.")

        self.root = self.design.rootComponent
    
    # ---------------------------------------------------------
    # Parse All Joints
    # ---------------------------------------------------------

    def parse(self):

        joints = []

        try:

            for joint in self.root.joints:

                joints.append(
                    self._parse_joint(joint)
                )

        except Exception as e:
            print(f"Error parsing joints: {str(e)}")
            print(traceback.format_exc())

        return joints

    # ---------------------------------------------------------
    # Parse Single Joint
    # ---------------------------------------------------------

    def _parse_joint(self, joint):

        parent = ""
        child = ""
        parent_transform = None
        child_transform = None

        try:

            parent = (
                joint.occurrenceOne.component.name
            )
            parent_transform = joint.occurrenceOne.transform2

        except Exception as e:
            parent = ""
            parent_transform = None
            # silently handle missing parent reference

        try:

            child = (
                joint.occurrenceTwo.component.name
            )
            child_transform = joint.occurrenceTwo.transform2

        except Exception as e:
            child = ""
            child_transform = None
            # silently handle missing child reference

        joint_type = self._joint_type(joint)

        origin = self._joint_origin(joint, parent_transform, child_transform)

        axis = self._joint_axis(joint)

        return {

            "name": joint.name,

            "type": joint_type,

            "parent": parent,

            "child": child,

            "origin": origin,

            "axis": axis

        }

    # ---------------------------------------------------------
    # Joint Type
    # ---------------------------------------------------------

    def _joint_type(self, joint):

        motion = joint.jointMotion

        if isinstance(
            motion,
            adsk.fusion.RevoluteJointMotion
        ):
            return "revolute"

        if isinstance(
            motion,
            adsk.fusion.SliderJointMotion
        ):
            return "prismatic"

        if isinstance(
            motion,
            adsk.fusion.RigidJointMotion
        ):
            return "fixed"

        if isinstance(
            motion,
            adsk.fusion.CylindricalJointMotion
        ):
            return "cylindrical"

        if isinstance(
            motion,
            adsk.fusion.PinSlotJointMotion
        ):
            return "planar"

        if isinstance(
            motion,
            adsk.fusion.BallJointMotion
        ):
            return "floating"

        return "fixed"

    # ---------------------------------------------------------
    # Joint Origin
    # ---------------------------------------------------------

    def _joint_origin(self, joint, parent_transform=None, child_transform=None):

        try:

            geometry = joint.geometry
            origin = geometry.origin
            fallback_origin = {
                "x": origin.x,
                "y": origin.y,
                "z": origin.z,
            }

            return compute_joint_origin(
                parent_transform,
                child_transform,
                fallback_origin=fallback_origin,
            )

        except Exception as e:
            # Return default origin if extraction fails
            return compute_joint_origin(
                parent_transform,
                child_transform,
                fallback_origin=None,
            )

    # ---------------------------------------------------------
    # Joint Axis
    # ---------------------------------------------------------

    def _joint_axis(self, joint):

        try:

            geometry = joint.geometry

            axis = geometry.primaryAxisVector

            return {

                "x": axis.x,
                "y": axis.y,
                "z": axis.z

            }

        except Exception as e:
            # Return default z-axis if extraction fails
            return {

                "x": 0.0,
                "y": 0.0,
                "z": 1.0

            }