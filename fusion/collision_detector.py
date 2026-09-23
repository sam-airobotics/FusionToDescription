"""Collision primitive extraction from Fusion 360 geometry."""


def detect_collision_shape(body):
    """Return a collision primitive in SI meters.

    Fusion 360 API geometry lengths are exposed in centimeters. URDF uses meters,
    so every exported dimension is converted here at the model boundary.
    """
    if not hasattr(body, "boundingBox"):
        raise ValueError(f"Expected body object with boundingBox property, got {type(body)}")

    bbox = body.boundingBox
    x = abs(bbox.maxPoint.x - bbox.minPoint.x) * 0.01
    y = abs(bbox.maxPoint.y - bbox.minPoint.y) * 0.01
    z = abs(bbox.maxPoint.z - bbox.minPoint.z) * 0.01

    dims = sorted((x, y, z))
    small, middle, large = dims
    tolerance = 0.0005

    if abs(x - y) < tolerance and abs(y - z) < tolerance:
        return {"shape": "Sphere", "radius": x / 2.0}

    if abs(middle - large) < tolerance:
        return {"shape": "Cylinder", "radius": middle / 2.0, "height": small}

    return {"shape": "Box", "length": large, "breadth": middle, "height": small}
