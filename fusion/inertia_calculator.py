"""Compute approximate link inertias from collision primitives."""


def calculate_inertia(shape, mass, geometry):
    """Calculate diagonal inertia tensor in kg*m^2.

    ``geometry`` is expected to already be normalized to SI meters by the
    collision detector/model builder.
    """
    if not isinstance(geometry, dict):
        raise ValueError(f"geometry must be a dict, got {type(geometry)}")
    if mass <= 0:
        return {"ixx": 0.0, "iyy": 0.0, "izz": 0.0, "ixy": 0.0, "iyz": 0.0, "ixz": 0.0}

    if shape == "Box":
        required = ("length", "breadth", "height")
        if not all(key in geometry for key in required):
            raise ValueError(f"Box geometry missing required keys. Got: {list(geometry.keys())}")
        l, b, h = (float(geometry[key]) for key in required)
        ixx = mass * (b * b + h * h) / 12.0
        iyy = mass * (l * l + h * h) / 12.0
        izz = mass * (l * l + b * b) / 12.0
    elif shape == "Cylinder":
        if not all(key in geometry for key in ("radius", "height")):
            raise ValueError(f"Cylinder geometry missing required keys. Got: {list(geometry.keys())}")
        r, h = float(geometry["radius"]), float(geometry["height"])
        ixx = mass * (3.0 * r * r + h * h) / 12.0
        iyy = ixx
        izz = 0.5 * mass * r * r
    elif shape == "Sphere":
        if "radius" not in geometry:
            raise ValueError(f"Sphere geometry missing 'radius' key. Got: {list(geometry.keys())}")
        inertia = 0.4 * mass * float(geometry["radius"]) ** 2
        ixx = iyy = izz = inertia
    else:
        return {"ixx": 1e-9, "iyy": 1e-9, "izz": 1e-9, "ixy": 0.0, "iyz": 0.0, "ixz": 0.0}

    return {"ixx": ixx, "iyy": iyy, "izz": izz, "ixy": 0.0, "iyz": 0.0, "ixz": 0.0}
