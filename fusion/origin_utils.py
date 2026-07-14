"""Conversions between Fusion transforms and URDF joint values.

Fusion stores distances in centimetres and joint geometry in the world frame.
URDF needs a transform from the parent link frame to the joint frame, with
distances in metres.  Keeping the Matrix3D until this boundary avoids losing
orientation information during parsing.
"""

import math


def matrix_to_urdf_origin(matrix):
    """Return a URDF ``origin`` dictionary from a parent-relative Matrix3D."""
    if matrix is None:
        raise ValueError("A parent-relative joint Matrix3D is required.")

    translation = matrix.translation
    r11 = matrix.getCell(0, 0)
    r21 = matrix.getCell(1, 0)
    r31 = matrix.getCell(2, 0)
    r32 = matrix.getCell(2, 1)
    r33 = matrix.getCell(2, 2)

    return {
        "x": translation.x / 100.0,
        "y": translation.y / 100.0,
        "z": translation.z / 100.0,
        "roll": math.atan2(r32, r33),
        "pitch": math.atan2(-r31, math.hypot(r11, r21)),
        "yaw": math.atan2(r21, r11),
    }


def axis_to_urdf(axis):
    """Convert a local axis tuple into the dictionary used by XML generators."""
    if axis is None:
        raise ValueError("A joint axis is required for a movable joint.")

    return {"x": axis[0], "y": axis[1], "z": axis[2]}
