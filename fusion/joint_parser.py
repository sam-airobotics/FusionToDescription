import traceback
import adsk.core
import adsk.fusion


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

        try:

            parent = (
                joint.occurrenceOne.component.name
            )

        except Exception as e:
            parent = ""
            # silently handle missing parent reference

        try:

            child = (
                joint.occurrenceTwo.component.name
            )

        except Exception as e:
            child = ""
            # silently handle missing child reference

        joint_type = self._joint_type(joint)

        origin = self._joint_origin(joint)

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

    def _joint_origin(self, joint):

        try:

            geometry = joint.geometry

            origin = geometry.origin

            return {

                "x": origin.x,
                "y": origin.y,
                "z": origin.z

            }

        except Exception as e:
            # Return default origin if extraction fails
            return {

                "x": 0.0,
                "y": 0.0,
                "z": 0.0

            }

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