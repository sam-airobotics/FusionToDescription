"""Utilities for converting Fusion transforms into URDF frame poses."""

import math


def _coerce_transform(transform):
    """Normalize a Fusion transform-like object into a plain dict."""
    if not transform:
        return None
    if isinstance(transform, dict):
        return transform
    translation = getattr(transform, "translation", None)
    if translation is None:
        return None
    rotation = getattr(transform, "rotation", None)
    if rotation is None:
        return {
            "translation": {"x": translation.x, "y": translation.y, "z": translation.z},
            "rotation": {
                "r11": transform.getCell(0, 0), "r12": transform.getCell(0, 1), "r13": transform.getCell(0, 2),
                "r21": transform.getCell(1, 0), "r22": transform.getCell(1, 1), "r23": transform.getCell(1, 2),
                "r31": transform.getCell(2, 0), "r32": transform.getCell(2, 1), "r33": transform.getCell(2, 2),
            },
        }
    return {
        "translation": {"x": translation.x, "y": translation.y, "z": translation.z},
        "rotation": {
            "r11": rotation.getCell(0, 0), "r12": rotation.getCell(0, 1), "r13": rotation.getCell(0, 2),
            "r21": rotation.getCell(1, 0), "r22": rotation.getCell(1, 1), "r23": rotation.getCell(1, 2),
            "r31": rotation.getCell(2, 0), "r32": rotation.getCell(2, 1), "r33": rotation.getCell(2, 2),
        },
    }


def _transpose_rotation(rotation):
    return {
        "r11": rotation["r11"], "r12": rotation["r21"], "r13": rotation["r31"],
        "r21": rotation["r12"], "r22": rotation["r22"], "r23": rotation["r32"],
        "r31": rotation["r13"], "r32": rotation["r23"], "r33": rotation["r33"],
    }


def _multiply_rotations(left, right):
    return {
        f"r{i}{j}": sum(left[f"r{i}{k}"] * right[f"r{k}{j}"] for k in (1, 2, 3))
        for i in (1, 2, 3) for j in (1, 2, 3)
    }


def _rotation_to_rpy(rotation):
    sy = math.sqrt(rotation["r11"] ** 2 + rotation["r21"] ** 2)
    if sy >= 1e-9:
        roll = math.atan2(rotation["r32"], rotation["r33"])
        pitch = math.atan2(-rotation["r31"], sy)
        yaw = math.atan2(rotation["r21"], rotation["r11"])
    else:
        roll = math.atan2(-rotation["r23"], rotation["r22"])
        pitch = math.atan2(-rotation["r31"], sy)
        yaw = 0.0
    return {"roll": roll, "pitch": pitch, "yaw": yaw}


def compute_relative_pose(parent_transform, target_transform, unit_scale=0.01):
    """Return parent inverse multiplied by target as an SI-meter URDF pose."""
    parent = _coerce_transform(parent_transform)
    target = _coerce_transform(target_transform)
    if not parent or not target:
        return {"x": 0.0, "y": 0.0, "z": 0.0, "roll": 0.0, "pitch": 0.0, "yaw": 0.0}

    delta = {
        axis: (target["translation"][axis] - parent["translation"][axis]) * unit_scale
        for axis in ("x", "y", "z")
    }
    parent_rotation_t = _transpose_rotation(parent["rotation"])
    relative_translation = {
        "x": parent_rotation_t["r11"] * delta["x"] + parent_rotation_t["r12"] * delta["y"] + parent_rotation_t["r13"] * delta["z"],
        "y": parent_rotation_t["r21"] * delta["x"] + parent_rotation_t["r22"] * delta["y"] + parent_rotation_t["r23"] * delta["z"],
        "z": parent_rotation_t["r31"] * delta["x"] + parent_rotation_t["r32"] * delta["y"] + parent_rotation_t["r33"] * delta["z"],
    }
    relative_rotation = _multiply_rotations(parent_rotation_t, target["rotation"])
    rpy = _rotation_to_rpy(relative_rotation)
    return {
        "x": round(relative_translation["x"], 9), "y": round(relative_translation["y"], 9), "z": round(relative_translation["z"], 9),
        "roll": round(rpy["roll"], 9), "pitch": round(rpy["pitch"], 9), "yaw": round(rpy["yaw"], 9),
    }


def transform_vector_to_frame(frame_transform, vector, normalize=True):
    """Express a world-space vector in the frame coordinates."""
    frame = _coerce_transform(frame_transform)
    if not frame:
        return {"x": vector["x"], "y": vector["y"], "z": vector["z"]}
    rotation_t = _transpose_rotation(frame["rotation"])
    result = {
        "x": rotation_t["r11"] * vector["x"] + rotation_t["r12"] * vector["y"] + rotation_t["r13"] * vector["z"],
        "y": rotation_t["r21"] * vector["x"] + rotation_t["r22"] * vector["y"] + rotation_t["r23"] * vector["z"],
        "z": rotation_t["r31"] * vector["x"] + rotation_t["r32"] * vector["y"] + rotation_t["r33"] * vector["z"],
    }
    if normalize:
        magnitude = math.sqrt(result["x"] ** 2 + result["y"] ** 2 + result["z"] ** 2)
        if magnitude <= 1e-12:
            raise ValueError("Cannot normalize a zero-length transform vector.")
        result = {axis: result[axis] / magnitude for axis in ("x", "y", "z")}
    return {"x": round(result["x"], 9), "y": round(result["y"], 9), "z": round(result["z"], 9)}


def compute_joint_origin(parent_transform, child_transform, joint_position=None, fallback_origin=None):
    """Backward-compatible joint-origin helper used by existing tests."""
    if joint_position is None:
        joint_position = fallback_origin
    parent = _coerce_transform(parent_transform)
    child = _coerce_transform(child_transform)
    if not parent:
        if joint_position:
            return {"x": joint_position["x"], "y": joint_position["y"], "z": joint_position["z"], "roll": 0.0, "pitch": 0.0, "yaw": 0.0}
        return {"x": 0.0, "y": 0.0, "z": 0.0, "roll": 0.0, "pitch": 0.0, "yaw": 0.0}
    if joint_position:
        target = {"translation": joint_position, "rotation": child["rotation"] if child else parent["rotation"]}
    elif child:
        target = child
    else:
        target = parent
    return compute_relative_pose(parent, target)
