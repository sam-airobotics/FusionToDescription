def detect_collision_shape(body):
    """Detect collision shape from a Fusion body.
    
    Args:
        body: Fusion bRepBody object with geometry
        
    Returns:
        Dict with detected shape ("Box", "Cylinder", "Sphere") and dimensions
    """
    if not hasattr(body, 'boundingBox'):
        raise ValueError(
            f"Expected body object with boundingBox property, got {type(body)}"
        )
    
    bbox = body.boundingBox

    x = abs(
        bbox.maxPoint.x -
        bbox.minPoint.x
    )

    y = abs(
        bbox.maxPoint.y -
        bbox.minPoint.y
    )

    z = abs(
        bbox.maxPoint.z -
        bbox.minPoint.z
    )

    dims = sorted([x, y, z])

    small = dims[0]
    middle = dims[1]
    large = dims[2]

    tolerance = 0.05

    # --------------------------------
    # Sphere
    # --------------------------------

    if (
        abs(x - y) < tolerance and
        abs(y - z) < tolerance
    ):

        return {
            "shape": "Sphere",
            "radius": x / 2.0
        }

    # --------------------------------
    # Cylinder
    # --------------------------------

    if abs(middle - large) < tolerance:

        return {
            "shape": "Cylinder",
            "radius": middle / 2.0,
            "height": small
        }

    # --------------------------------
    # Box
    # --------------------------------

    return {
        "shape": "Box",
        "length": large,
        "breadth": middle,
        "height": small
    }