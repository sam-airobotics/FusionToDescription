from __future__ import annotations

import math
import traceback
from typing import Any

import adsk.core
import adsk.fusion

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
    """Parse Fusion joints into occurrence-consistent ROS joint records."""

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

        return {
            "name": _sanitize_name(joint.name),
            "fusion_name": joint.name,
            "type": self.TYPE_NAMES[fusion_type],
            "parent": self._occurrence_name(second),
            "child": self._occurrence_name(first),
            "parent_path": self._occurrence_path(second),
            "child_path": self._occurrence_path(first),
            "origin": self._joint_origin(joint, second, first, fusion_type),
            "axis": self._joint_axis(joint, fusion_type),
            "limits": self._joint_limits(joint, fusion_type),
        }

    @staticmethod
    def _occurrence(joint, attr):
        try:
            return getattr(joint, attr)
        except (AttributeError, RuntimeError):
            return None

    @staticmethod
    def _occurrence_path(occurrence):
        return getattr(occurrence, "fullPathName", None) or getattr(
            getattr(occurrence, "component", None), "name", ""
        )

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
    def _origin_geometry(joint):
        try:
            geometry = joint.geometry
            if geometry is not None:
                return geometry
        except (AttributeError, RuntimeError):
            pass
        for attr in ("geometryOrOriginTwo", "geometryOrOriginOne"):
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

    @classmethod
    def _joint_origin(cls, joint, parent_occurrence, child_occurrence, fusion_type):
        geometry = cls._origin_geometry(joint)
        if geometry is None:
            if fusion_type == 0:
                return cls._relative_pose(parent_occurrence.transform2, child_occurrence.transform2)
            raise ValueError(f"Joint '{joint.name}' has no usable origin geometry.")
        point = geometry.origin
        return cls._compute_joint_origin(
            cls._matrix_dict(parent_occurrence.transform2),
            cls._matrix_dict(child_occurrence.transform2),
            {"x": point.x, "y": point.y, "z": point.z},
        )

    @staticmethod
    def _joint_axis(joint, fusion_type):
        if fusion_type == 0:
            return {"x": 0.0, "y": 0.0, "z": 1.0}
        motion = joint.jointMotion
        vector = motion.rotationAxisVector if fusion_type == 1 else motion.slideDirectionVector
        magnitude = math.sqrt(vector.x ** 2 + vector.y ** 2 + vector.z ** 2)
        if magnitude <= 1e-12:
            raise ValueError(f"Joint '{joint.name}' has a zero-length motion axis.")
        return {"x": round(vector.x / magnitude, 6), "y": round(vector.y / magnitude, 6), "z": round(vector.z / magnitude, 6)}

    @staticmethod
    def _joint_limits(joint, fusion_type):
        if fusion_type == 0:
            return {}
        motion = joint.jointMotion
        limits = motion.rotationLimits if fusion_type == 1 else motion.slideLimits
        if limits is None:
            return {}
        try:
            # Disabled minimum/maximum limits mean the joint is unbounded.
            if not limits.isMinimumValueEnabled or not limits.isMaximumValueEnabled:
                return {}
            lower = float(limits.minimumValue)
            upper = float(limits.maximumValue)
            if not (math.isfinite(lower) and math.isfinite(upper)) or lower > upper:
                return {}
            if fusion_type == 2:
                lower *= 0.01
                upper *= 0.01
            # Never turn an unconfigured limit into 0..0; URDF can represent an
            # unbounded revolute/prismatic joint by omitting <limit> entirely.
            return {"lower": round(lower, 9), "upper": round(upper, 9), "effort": 1000.0, "velocity": 100.0}
        except (AttributeError, RuntimeError, TypeError, ValueError):
            return {}

    @staticmethod
    def _matrix_dict(matrix):
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
    def _transpose(r):
        return {"r11": r["r11"], "r12": r["r21"], "r13": r["r31"], "r21": r["r12"], "r22": r["r22"], "r23": r["r32"], "r31": r["r13"], "r32": r["r23"], "r33": r["r33"]}

    @staticmethod
    def _multiply_rotation(a, b):
        return {f"r{i}{j}": sum(a[f"r{i}{k}"] * b[f"r{k}{j}"] for k in (1, 2, 3)) for i in (1, 2, 3) for j in (1, 2, 3)}

    @staticmethod
    def _rotate(r, v):
        return {
            "x": r["r11"] * v["x"] + r["r12"] * v["y"] + r["r13"] * v["z"],
            "y": r["r21"] * v["x"] + r["r22"] * v["y"] + r["r23"] * v["z"],
            "z": r["r31"] * v["x"] + r["r32"] * v["y"] + r["r33"] * v["z"],
        }

    @classmethod
    def _compute_joint_origin(cls, parent, child, joint_position):
        delta = {axis: (joint_position[axis] - parent["translation"][axis]) * 0.01 for axis in ("x", "y", "z")}
        parent_rt = cls._transpose(parent["rotation"])
        translation = cls._rotate(parent_rt, delta)
        rotation = cls._multiply_rotation(parent_rt, child["rotation"])
        return cls._pose(translation, rotation)

    @classmethod
    def _relative_pose(cls, parent_matrix, child_matrix):
        parent = cls._matrix_dict(parent_matrix)
        child = cls._matrix_dict(child_matrix)
        delta = {axis: (child["translation"][axis] - parent["translation"][axis]) * 0.01 for axis in ("x", "y", "z")}
        parent_rt = cls._transpose(parent["rotation"])
        return cls._pose(cls._rotate(parent_rt, delta), cls._multiply_rotation(parent_rt, child["rotation"]))

    @staticmethod
    def _pose(translation, rotation):
        r11, r21, r31 = rotation["r11"], rotation["r21"], rotation["r31"]
        sy = math.sqrt(r11 * r11 + r21 * r21)
        if sy >= 1e-6:
            roll = math.atan2(rotation["r32"], rotation["r33"])
            pitch = math.atan2(-r31, sy)
            yaw = math.atan2(r21, r11)
        else:
            roll = math.atan2(-rotation["r23"], rotation["r22"])
            pitch = math.atan2(-r31, sy)
            yaw = 0.0
        return {
            "x": round(translation["x"], 9), "y": round(translation["y"], 9), "z": round(translation["z"], 9),
            "roll": round(roll, 9), "pitch": round(pitch, 9), "yaw": round(yaw, 9),
        }
