from .collision_detector import detect_collision_shape

import adsk.core


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


def get_component_data():
    """Extract visible leaf occurrences as URDF links.

    Link identity is occurrence-based, matching the joint parser. The component
    name is retained for mesh/material lookup while ``name`` is the unique ROS
    link/frame name derived from ``fullPathName``.
    """
    app = adsk.core.Application.get()
    design = app.activeProduct
    data = []
    if not design:
        return data

    root = design.rootComponent
    for occ in root.allOccurrences:
        try:
            component = occ.component
            if component.bRepBodies.count == 0:
                continue
            if not occ.isLightBulbOn:
                continue
            if occ.childOccurrences.count > 0:
                continue
            if occ.component.joints.count > 0:
                continue

            body = component.bRepBodies.item(0)
            name = "base_link" if component.name == "base_link" else _sanitize_name(occ.fullPathName)
            data.append({
                "name": name,
                "component_name": component.name,
                "occurrence_path": occ.fullPathName,
                "mesh": f"{name}.stl",
                "collision": detect_collision_shape(body),
            })
        except Exception:
            continue

    return data
