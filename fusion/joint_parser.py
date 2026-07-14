"""Parse Fusion Joint and AsBuiltJoint objects into kinematic data."""

import adsk.core
import adsk.fusion


app = adsk.core.Application.get()


class JointParser:
    def __init__(self):
        self.design = app.activeProduct
        if not isinstance(self.design, adsk.fusion.Design):
            raise RuntimeError("No active Fusion Design.")
        self.root = self.design.rootComponent

    def parse(self):
        """Parse joints throughout the design, including subassemblies."""
        # root.joints contains only joints created on the root component.
        joints = getattr(self.root, "allJoints", None)
        if joints is None:
            joints = self.root.joints
        return [self._parse_joint(joint) for joint in joints]

    def _parse_joint(self, joint):
        # Fusion's occurrenceOne is the moving side.  URDF's parent is the
        # grounded side, occurrenceTwo, and its child is occurrenceOne.
        try:
            parent_occurrence = joint.occurrenceTwo
            child_occurrence = joint.occurrenceOne
            parent = parent_occurrence.component.name
            child = child_occurrence.component.name
        except AttributeError as error:
            raise RuntimeError(
                f"Joint '{joint.name}' has no valid parent/child occurrences."
            ) from error

        limits = self._joint_limits(joint)
        joint_type = self._joint_type(joint, limits)
        joint_frame = self._joint_frame(joint)
        origin_transform = self._relative_transform(
            parent_occurrence.transform2, joint_frame, joint.name
        )

        return {
            "name": joint.name,
            "type": joint_type,
            "parent": parent,
            "child": child,
            # Retain Matrix3D objects until URDF generation.  They are the
            # authoritative source for position and orientation.
            "joint_frame": joint_frame,
            "origin_transform": origin_transform,
            "axis": self._joint_axis(joint, joint_frame, joint_type),
            "limits": limits,
        }

    def _joint_type(self, joint, limits):
        motion = joint.jointMotion
        if isinstance(motion, adsk.fusion.RevoluteJointMotion):
            return "revolute" if limits else "continuous"
        if isinstance(motion, adsk.fusion.SliderJointMotion):
            return "prismatic"
        if isinstance(motion, adsk.fusion.RigidJointMotion):
            return "fixed"
        if isinstance(motion, adsk.fusion.CylindricalJointMotion):
            return "cylindrical"
        if isinstance(motion, adsk.fusion.PinSlotJointMotion):
            return "planar"
        if isinstance(motion, adsk.fusion.BallJointMotion):
            return "floating"
        return "fixed"

    @staticmethod
    def _joint_limits(joint):
        """Return enabled limits in URDF units (metres and radians)."""
        motion = joint.jointMotion
        if isinstance(motion, adsk.fusion.RevoluteJointMotion):
            limits, scale = motion.rotationLimits, 1.0
        elif isinstance(motion, adsk.fusion.SliderJointMotion):
            limits, scale = motion.slideLimits, 0.01  # Fusion centimetres.
        else:
            return {}

        if not (
            limits.isMinimumValueEnabled and limits.isMaximumValueEnabled
        ):
            return {}
        return {
            "lower": limits.minimumValue * scale,
            "upper": limits.maximumValue * scale,
        }

    def _joint_frame(self, joint):
        """Build the world-frame Matrix3D for a Joint or AsBuiltJoint."""
        geometry = self._joint_geometry(joint)
        try:
            frame = adsk.core.Matrix3D.create()
            frame.setWithCoordinateSystem(
                geometry.origin,
                geometry.secondaryAxisVector,
                geometry.thirdAxisVector,
                geometry.primaryAxisVector,
            )
            return frame
        except AttributeError as error:
            raise RuntimeError(
                f"Joint '{joint.name}' does not expose a usable origin and axes."
            ) from error

    @staticmethod
    def _joint_geometry(joint):
        """Return geometry from either Fusion joint API without a fallback."""
        if hasattr(joint, "geometry"):
            geometry = joint.geometry
        else:
            geometry = getattr(joint, "geometryOrOriginTwo", None)
            # An AsBuiltJoint can return a JointOrigin; unwrap its geometry.
            if geometry is not None and hasattr(geometry, "geometry"):
                geometry = geometry.geometry

        if geometry is None:
            raise RuntimeError(
                f"Joint '{joint.name}' has no joint geometry or joint origin."
            )
        return geometry

    @staticmethod
    def _relative_transform(parent_transform, joint_frame, joint_name):
        """Calculate parent^-1 * joint while retaining Matrix3D precision."""
        try:
            relative = parent_transform.copy()
            if not relative.invert():
                raise RuntimeError("parent transform is not invertible")
            relative.transformBy(joint_frame)
            return relative
        except Exception as error:
            raise RuntimeError(
                f"Unable to compute parent-relative transform for joint '{joint_name}'."
            ) from error

    def _joint_axis(self, joint, joint_frame, joint_type):
        """Express Fusion's world-frame motion axis in joint coordinates."""
        if joint_type == "fixed":
            return None

        motion = joint.jointMotion
        if joint_type in ("revolute", "continuous", "cylindrical", "planar"):
            axis = getattr(motion, "rotationAxisVector", None)
        elif joint_type == "prismatic":
            axis = getattr(motion, "slideDirectionVector", None)
        else:
            axis = None
        if axis is None:
            raise RuntimeError(f"Joint '{joint.name}' has no motion axis.")

        # R_joint^T * axis_world
        return (
            joint_frame.getCell(0, 0) * axis.x + joint_frame.getCell(1, 0) * axis.y + joint_frame.getCell(2, 0) * axis.z,
            joint_frame.getCell(0, 1) * axis.x + joint_frame.getCell(1, 1) * axis.y + joint_frame.getCell(2, 1) * axis.z,
            joint_frame.getCell(0, 2) * axis.x + joint_frame.getCell(1, 2) * axis.y + joint_frame.getCell(2, 2) * axis.z,
        )
