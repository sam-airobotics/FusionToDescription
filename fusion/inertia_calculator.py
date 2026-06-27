import math


def calculate_inertia(shape, mass, geometry):
    """Calculate inertia tensor for a given shape and mass.
    
    Args:
        shape: Shape type ("Box", "Cylinder", "Sphere")
        mass: Mass in kg
        geometry: Dict with geometry parameters
        
    Returns:
        Dict with ixx, iyy, izz inertia components
    """
    if not isinstance(geometry, dict):
        raise ValueError(f"geometry must be a dict, got {type(geometry)}")
        
    if shape == "Box":
        if not all(k in geometry for k in ["length", "breadth", "height"]):
            raise ValueError(
                f"Box geometry missing required keys. Got: {list(geometry.keys())}"
            )
        l = geometry["length"]
        b = geometry["breadth"]
        h = geometry["height"]

        ixx = (1.0 / 12.0) * mass * (b*b + h*h)
        iyy = (1.0 / 12.0) * mass * (l*l + h*h)
        izz = (1.0 / 12.0) * mass * (l*l + b*b)

        return {
            "ixx": ixx,
            "iyy": iyy,
            "izz": izz
        }

    elif shape == "Cylinder":
        if not all(k in geometry for k in ["radius", "height"]):
            raise ValueError(
                f"Cylinder geometry missing required keys. Got: {list(geometry.keys())}"
            )
        r = geometry["radius"]
        h = geometry["height"]

        ixx = (1.0 / 12.0) * mass * (
            3*r*r + h*h
        )

        iyy = ixx

        izz = 0.5 * mass * r*r

        return {
            "ixx": ixx,
            "iyy": iyy,
            "izz": izz
        }

    elif shape == "Sphere":
        if "radius" not in geometry:
            raise ValueError(
                f"Sphere geometry missing 'radius' key. Got: {list(geometry.keys())}"
            )
        r = geometry["radius"]

        inertia = (
            2.0 / 5.0
        ) * mass * r*r

        return {
            "ixx": inertia,
            "iyy": inertia,
            "izz": inertia
        }

    return {
        "ixx": 0.0,
        "iyy": 0.0,
        "izz": 0.0
    }