def detect_collision_shape(body, forced_shape=None):
    """
    Detect collision geometry or use a user-selected shape.

    Args:
        body: Fusion BRepBody
        forced_shape: Optional ("Box", "Cylinder", "Sphere")

    Returns:
        dict
    """

    bbox = body.boundingBox

    scale = 0.01

    x = abs(bbox.maxPoint.x - bbox.minPoint.x) * scale
    y = abs(bbox.maxPoint.y - bbox.minPoint.y) * scale
    z = abs(bbox.maxPoint.z - bbox.minPoint.z) * scale

    dims = sorted([x, y, z])

    small = dims[0]
    middle = dims[1]
    large = dims[2]

    # -----------------------------
    # User override
    # -----------------------------

    if forced_shape == "Box":
        return {
            "shape": "Box",
            "length": large,
            "breadth": middle,
            "height": small
        }

    elif forced_shape == "Cylinder":
        return {
            "shape": "Cylinder",
            "radius": middle / 2,
            "height": small
        }

    elif forced_shape == "Sphere":
        return {
            "shape": "Sphere",
            "radius": large / 2
        }

    # -----------------------------
    # Automatic Detection
    # -----------------------------

    tolerance = 0.05

    if (
        abs(x-y) < tolerance and
        abs(y-z) < tolerance
    ):
        return {
            "shape":"Sphere",
            "radius":large/2
        }

    elif abs(middle-large) < tolerance:
        return {
            "shape":"Cylinder",
            "radius":middle/2,
            "height":small
        }

    return {
        "shape":"Box",
        "length":large,
        "breadth":middle,
        "height":small
    }
