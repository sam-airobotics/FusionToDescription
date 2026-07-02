"""Utilities for converting Fusion transforms into URDF joint origins."""

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
            "translation": {
                "x": translation.x,
                "y": translation.y,
                "z": translation.z,
            },
            "rotation": {
                "r11": transform.getCell(0, 0),
                "r12": transform.getCell(0, 1),
                "r13": transform.getCell(0, 2),
                "r21": transform.getCell(1, 0),
                "r22": transform.getCell(1, 1),
                "r23": transform.getCell(1, 2),
                "r31": transform.getCell(2, 0),
                "r32": transform.getCell(2, 1),
                "r33": transform.getCell(2, 2),
            },
        }

    return {
        "translation": {
            "x": translation.x,
            "y": translation.y,
            "z": translation.z,
        },
        "rotation": {
            "r11": rotation.getCell(0, 0),
            "r12": rotation.getCell(0, 1),
            "r13": rotation.getCell(0, 2),
            "r21": rotation.getCell(1, 0),
            "r22": rotation.getCell(1, 1),
            "r23": rotation.getCell(1, 2),
            "r31": rotation.getCell(2, 0),
            "r32": rotation.getCell(2, 1),
            "r33": rotation.getCell(2, 2),
        },
    }


def _transpose_rotation(rotation):
    return {
        "r11": rotation["r11"],
        "r12": rotation["r21"],
        "r13": rotation["r31"],
        "r21": rotation["r12"],
        "r22": rotation["r22"],
        "r23": rotation["r32"],
        "r31": rotation["r13"],
        "r32": rotation["r23"],
        "r33": rotation["r33"],
    }


def _multiply_rotations(left, right):
    return {
        "r11": left["r11"] * right["r11"] + left["r12"] * right["r21"] + left["r13"] * right["r31"],
        "r12": left["r11"] * right["r12"] + left["r12"] * right["r22"] + left["r13"] * right["r32"],
        "r13": left["r11"] * right["r13"] + left["r12"] * right["r23"] + left["r13"] * right["r33"],
        "r21": left["r21"] * right["r11"] + left["r22"] * right["r21"] + left["r23"] * right["r31"],
        "r22": left["r21"] * right["r12"] + left["r22"] * right["r22"] + left["r23"] * right["r32"],
        "r23": left["r21"] * right["r13"] + left["r22"] * right["r23"] + left["r23"] * right["r33"],
        "r31": left["r31"] * right["r11"] + left["r32"] * right["r21"] + left["r33"] * right["r31"],
        "r32": left["r31"] * right["r12"] + left["r32"] * right["r22"] + left["r33"] * right["r32"],
        "r33": left["r31"] * right["r13"] + left["r32"] * right["r23"] + left["r33"] * right["r33"],
    }


def _rotation_to_rpy(rotation):
    roll = math.atan2(rotation["r32"], rotation["r33"])
    pitch = math.atan2(-rotation["r31"], math.sqrt(rotation["r32"] ** 2 + rotation["r33"] ** 2))
    yaw = math.atan2(rotation["r21"], rotation["r11"])
    return {"roll": roll, "pitch": pitch, "yaw": yaw}


def compute_joint_origin(
    parent_transform,
    child_transform,
    joint_position=None,
):
    """
    Compute a joint origin expressed in the parent link frame.

    Args:
        parent_transform: Fusion transform of parent occurrence.
        child_transform: Fusion transform of child occurrence.
        joint_position: Dict {"x","y","z"} representing the Fusion joint
                        geometry origin in world coordinates.

    Returns:
        dict containing xyz and rpy.
    """

    parent = _coerce_transform(parent_transform)
    child = _coerce_transform(child_transform)

    if parent:

        parent_translation = parent["translation"]
        parent_rotation = parent["rotation"]

        # --------------------------------------------------
        # Translation
        # --------------------------------------------------

        if joint_position:

            delta = {
                "x": joint_position["x"] - parent_translation["x"],
                "y": joint_position["y"] - parent_translation["y"],
                "z": joint_position["z"] - parent_translation["z"],
            }

        elif child:

            child_translation = child["translation"]

            delta = {
                "x": child_translation["x"] - parent_translation["x"],
                "y": child_translation["y"] - parent_translation["y"],
                "z": child_translation["z"] - parent_translation["z"],
            }

        else:

            delta = {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
            }

        # Convert world coordinates into the parent's frame.
        parent_rotation_t = _transpose_rotation(parent_rotation)

        relative_translation = {
            "x": parent_rotation_t["r11"] * delta["x"]
               + parent_rotation_t["r12"] * delta["y"]
               + parent_rotation_t["r13"] * delta["z"],

            "y": parent_rotation_t["r21"] * delta["x"]
               + parent_rotation_t["r22"] * delta["y"]
               + parent_rotation_t["r23"] * delta["z"],

            "z": parent_rotation_t["r31"] * delta["x"]
               + parent_rotation_t["r32"] * delta["y"]
               + parent_rotation_t["r33"] * delta["z"],
        }

        # --------------------------------------------------
        # Rotation
        # --------------------------------------------------

        if child:

            child_rotation = child["rotation"]

            relative_rotation = _multiply_rotations(
                parent_rotation_t,
                child_rotation,
            )

            rpy = _rotation_to_rpy(relative_rotation)

        else:

            rpy = {
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": 0.0,
            }

        return {
            "x": relative_translation["x"],
            "y": relative_translation["y"],
            "z": relative_translation["z"],
            **rpy,
        }

    # --------------------------------------------------
    # Fallback
    # --------------------------------------------------

    if joint_position:

        return {
            "x": joint_position["x"],
            "y": joint_position["y"],
            "z": joint_position["z"],
            "roll": 0.0,
            "pitch": 0.0,
            "yaw": 0.0,
        }

    return {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0,
        "roll": 0.0,
        "pitch": 0.0,
        "yaw": 0.0,
    }