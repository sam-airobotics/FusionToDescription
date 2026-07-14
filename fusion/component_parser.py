from .collision_detector import (
    get_body_dimensions,
    build_collision
)

import adsk.core


def get_component_data():
    """Extract component data including dimensions, collision and mesh info."""

    app = adsk.core.Application.get()
    design = app.activeProduct

    if not design:
        return []

    data = []

    root = design.rootComponent

    for occ in root.occurrences:

        component = occ.component

        if component.bRepBodies.count == 0:
            continue

        body = component.bRepBodies.item(0)

        dimensions = get_body_dimensions(body)

        collision = build_collision(
            dimensions,
            "Box"      # default shape (or auto-detected if you keep that feature)
        )

        mesh_filename = f"{component.name}.stl"

        data.append({
            "name": component.name,
            "body": body,
            "mesh": mesh_filename,
            "dimensions": dimensions,
            "collision": collision
        })

    return data
