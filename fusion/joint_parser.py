from __future__ import annotations

import math
import traceback
from typing import Any

import adsk.core
import adsk.fusion

from .origin_utils import compute_relative_pose, transform_vector_to_frame

app = adsk.core.Application.get()


def _sanitize_name(value):
    result = str(value or "")
    for char in ("/", "\\", " ", ":", "-", "."):
        result = result.replace(char, "_")
    while "__" in result:
        result = result.replace("__", "_")
    result = result.strip("_") or "unnamed"
    if not result[0].isalpha():
        result = f"link_{result}"
    return result


class JointParser:
    """Parse Fusion joints into frame-correct ROS joint records.

    Fusion occurrences define link frames. Fusion joint geometry defines the
    joint frame. The exporter keeps those two frames separate: the joint
    origin is parent->joint, while the child link visual/collision origin is
    joint->child. This avoids applying an occurrence transform twice.
    """

    TYPE_NAMES = {0: "fixed", 1: "revolute", 2: "prismatic"}
    SUPPORTED_TYPES = {0, 1, 2}

    def __init__(self) -> None:
        self.design = app.activeProduct
        if not isinstance(self.design, adsk.fusion.Design):
            raise RuntimeError("No active Fusion Design.")
        self.root = self.design.rootComponent

    def parse(self) -> list[dict[str, Any]]:
        parsed = []
        joints = list(self.root.allJoints) + list(self.root.allAsBuiltJoints)
        for joint in joints:
            try:
                parsed.append(self._parse_joint(joint))
            except Exception as exc:
                print(f"Error parsing joint '{getattr(joint, 'name', '<unnamed>')}': {exc}")
                print(traceback.format_exc())
        return parsed

    def _parse_joint(self, joint) -> dict[str, Any]:
        first = self._occurrence(joint, "occurrenceOne")
        second = self._occurrence(joint, "occurrenceTwo")
        if first is None or second is None:
            raise ValueError(
                f"Joint '{joint.name}' is not between two component occurrences. "
                "Create the joint between component occurrences; grounded/root geometry "
                "should be represented by a base_link component."
            )

        fusion_type = self._joint_type_code(joint)
        if fusion_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"Joint '{joint.name}' uses unsupported Fusion type '{fusion_type}'.")

        first_frame = self._matrix_dict(first.transform2)
        second_frame = self._matrix_dict(second.transform2)
        joint_frame = self._joint_frame(joint, fusion_type)

        record = {
            "name": _sanitize_name(joint.name),
            "fusion_name": joint.name,
            "type": self.TYPE_NAMES[fusion_type],
            "parent": self._occurrence_name(second),
            "child": self._occurrence_name(first),
            "parent_path": self._occurrence_path(second),
            "child_path": self._occurrence_path(first),
            "_parent_frame": second_frame,
            "_child_frame": first_frame,
            "_joint_frame": joint_frame,
            "_axis_world": self._motion_axis(joint, fusion_type),
            "origin": {},
            "axis": {},
            "limits": self._joint_limits(joint, fusion_type),
        }
        self._finalize_record(record)
        return record

    @staticmethod
    def _occurrence(joint, attr):
        try:
            return getattr(joint, attr)
        except (AttributeError, RuntimeError):
            return None

    @staticmethod
    def _occurrence_path(occurrence):
        return getattr(occurrence, "fullPathName", None) or getattr(getattr(occurrence, "component", None), "name", "")

    @staticmethod
    def _occurrence_name(occurrence):
        component_name = getattr(getattr(occurrence, "component", None), "name", "")
        if component_name == "base_link":
            return "base_link"
        return _sanitize_name(JointParser._occurrence_path(occurrence) or component_name)

    @staticmethod
    def _joint_type_code(joint):
        motion = joint.jointMotion
        try:
            return int(motion.jointType)
        except (AttributeError, TypeError, ValueError, RuntimeError):
            for motion_class, code in (
                (adsk.fusion.RigidJointMotion, 0),
                (adsk.fusion.RevoluteJointMotion, 1),
                (adsk.fusion.SliderJointMotion, 2),
            ):
                if isinstance(motion, motion_class):
                    return code
        raise ValueError(f"Unable to determine joint type for '{joint.name}'.")

    @staticmethod
    def _matrix_dict(matrix):
        if matrix is None:
            return None
        translation = matrix.translation
        return {
            "translation": {"x": translation.x, "y": translation.y, "z": translation.z},
            "rotation": {
                "r11": matrix.getCell(0, 0), "r12": matrix.getCell(0, 1), "r13": matrix.getCell(0, 2),
                "r21": matrix.getCell(1, 0), "r22": matrix.getCell(1, 1), "r23": matrix.getCell(1, 2),
                "r31": matrix.getCell(2, 0), "r32": matrix.getCell(2, 1), "r33": matrix.getCell(2, 2),
            },
        }

    @staticmethod
    def _vector_dict(vector):
        if vector is None:
            return None
        return {"x": float(vector.x), "y": float(vector.y), "z": float(vector.z)}

    @classmethod
    def _frame_from_geometry(cls, geometry):
        if geometry is None:
            return None
        try:
            transform = getattr(geometry, "transform", None)
            if transform is not None:
                frame = cls._matrix_dict(transform)
                if frame is not None:
                    return frame
        except (AttributeError, RuntimeError):
            pass
        try:
            origin = geometry.origin
            x_axis = geometry.secondaryAxisVector
            y_axis = geometry.thirdAxisVector
            z_axis = geometry.primaryAxisVector
        except (AttributeError, RuntimeError):
            return None
        if any(value is None for value in (origin, x_axis, y_axis, z_axis)):
            return None
        return {
            "translation": {"x": origin.x, "y": origin.y, "z": origin.z},
            "rotation": {
                "r11": x_axis.x, "r12": y_axis.x, "r13": z_axis.x,
                "r21": x_axis.y, "r22": y_axis.y, "r23": z_axis.y,
                "r31": x_axis.z, "r32": y_axis.z, "r33": z_axis.z,
            },
        }

    @classmethod
    def _joint_frame(cls, joint, fusion_type):
        for attr in ("geometryOneTransform", "geometryTwoTransform"):
            try:
                frame = cls._matrix_dict(getattr(joint, attr))
            except (AttributeError, RuntimeError):
                frame = None
            if frame is not None:
                return frame
        try:
            frame = cls._matrix_dict(getattr(joint, "transform"))
        except (AttributeError, RuntimeError):
            frame = None
        if frame is not None:
            return frame
        for attr in ("geometryOrOriginOne", "geometryOrOriginTwo"):
            try:
                entity = getattr(joint, attr)
            except (AttributeError, RuntimeError):
                continue
            frame = cls._frame_from_geometry(entity)
            if frame is not None:
                return frame
        return cls._frame_from_geometry(cls._origin_geometry(joint))

    @staticmethod
    def _origin_geometry(joint):
        try:
            geometry = joint.geometry
            if geometry is not None:
                return geometry
        except (AttributeError, RuntimeError):
            pass
        for attr in ("geometryOrOriginOne", "geometryOrOriginTwo"):
            try:
                value = getattr(joint, attr)
            except (AttributeError, RuntimeError):
                continue
            if value is None:
                continue
            try:
                if isinstance(value, adsk.fusion.JointOrigin):
                    return value.geometry
            except (AttributeError, RuntimeError):
                pass
            return value
        return None

    @staticmethod
    def _motion_axis(joint, fusion_type):
        if fusion_type == 0:
            return {"x": 0.0, "y": 0.0, "z": 1.0}
        motion = joint.jointMotion
        vector = motion.rotationAxisVector if fusion_type == 1 else motion.slideDirectionVector
        if vector is None:
            raise ValueError(f"Joint '{joint.name}' has no usable motion axis vector.")
        axis = JointParser._vector_dict(vector)
        magnitude = math.sqrt(axis["x"] ** 2 + axis["y"] ** 2 + axis["z"] ** 2)
        if magnitude <= 1e-12:
            raise ValueError(f"Joint '{joint.name}' has a zero-length motion axis.")
        return {key: axis[key] / magnitude for key in ("x", "y", "z")}

    @staticmethod
    def _joint_limits(joint, fusion_type):
        if fusion_type == 0:
            return {}
        motion = joint.jointMotion
        limits = motion.rotationLimits if fusion_type == 1 else motion.slideLimits
        if limits is None:
            return {}
        try:
            if not limits.isMinimumValueEnabled or not limits.isMaximumValueEnabled:
                return {}
            lower = float(limits.minimumValue)
            upper = float(limits.maximumValue)
            if not math.isfinite(lower) or not math.isfinite(upper) or lower > upper:
                return {}
            if fusion_type == 2:
                lower *= 0.01
                upper *= 0.01
            return {"lower": round(lower, 9), "upper": round(upper, 9), "effort": 1000.0, "velocity": 100.0}
        except (AttributeError, RuntimeError, TypeError, ValueError):
            return {}

    @classmethod
    def _finalize_record(cls, record):
        parent_frame = record.get("_parent_frame")
        child_frame = record.get("_child_frame")
        joint_frame = record.get("_joint_frame") or child_frame

        if parent_frame is not None and joint_frame is not None:
            record["origin"] = compute_relative_pose(parent_frame, joint_frame)
        else:
            record["origin"] = {"x": 0.0, "y": 0.0, "z": 0.0, "roll": 0.0, "pitch": 0.0, "yaw": 0.0}

        if record["type"] in ("revolute", "prismatic"):
            axis_world = record.get("_axis_world")
            record["axis"] = (
                transform_vector_to_frame(joint_frame, axis_world, normalize=True)
                if axis_world is not None and joint_frame is not None
                else {"x": 0.0, "y": 0.0, "z": 1.0}
            )
        else:
            record["axis"] = {"x": 0.0, "y": 0.0, "z": 1.0}

        if joint_frame is not None and child_frame is not None:
            record["_child_origin"] = compute_relative_pose(joint_frame, child_frame)
        else:
            record["_child_origin"] = {"x": 0.0, "y": 0.0, "z": 0.0, "roll": 0.0, "pitch": 0.0, "yaw": 0.0}
        return record

    @classmethod
    def finalize_records(cls, records):
        """Recompute frame-dependent data after parent/child orientation."""
        for record in records:
            cls._finalize_record(record)
        return records
