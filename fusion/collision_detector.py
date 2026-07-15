"""
Utilities for collision primitive generation.
"""


def get_body_dimensions(body):
    """
    Extract body dimensions from a Fusion BRepBody.

    Returns:
        {
            "length": float,
            "breadth": float,
            "height": float
        }
    """

    bbox = body.boundingBox

    scale = 0.01

    x = abs(bbox.maxPoint.x - bbox.minPoint.x) * scale
    y = abs(bbox.maxPoint.y - bbox.minPoint.y) * scale
    z = abs(bbox.maxPoint.z - bbox.minPoint.z) * scale

    dims = sorted([x, y, z])

    return {
        "length": dims[2],
        "breadth": dims[1],
        "height": dims[0]
    }


def auto_detect_shape(dimensions):
    """
    Automatically determine the best primitive shape.

    Returns:
        "Box", "Cylinder" or "Sphere"
    """

    length = dimensions["length"]
    breadth = dimensions["breadth"]
    height = dimensions["height"]

    tolerance = 0.05

    if (
        abs(length - breadth) < tolerance and
        abs(breadth - height) < tolerance
    ):
        return "Sphere"

    if abs(length - breadth) < tolerance:
        return "Cylinder"

    return "Box"


def build_collision(dimensions, shape):
    """
    Build collision parameters from dimensions.

    Args:
        dimensions: Dictionary returned by get_body_dimensions()
        shape: Box, Cylinder or Sphere

    Returns:
        Collision dictionary
    """

    length = dimensions["length"]
    breadth = dimensions["breadth"]
    height = dimensions["height"]

    if shape == "Box":
        return {
            "shape": "Box",
            "length": length,
            "breadth": breadth,
            "height": height
        }

    if shape == "Cylinder":
        return {
            "shape": "Cylinder",
            "radius": breadth / 2.0,
            "height": height
        }

    if shape == "Sphere":
        return {
            "shape": "Sphere",
            "radius": max(length, breadth, height) / 2.0
        }

    raise ValueError(f"Unsupported collision shape: {shape}")
