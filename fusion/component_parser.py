from .collision_detector import (
    detect_collision_shape
)

import adsk.core
from ..utils.logger import Logger


def get_component_data():
    """Extract component data including collision and mesh info.
    
    Returns:
        List of dicts with component name, collision, and mesh filename
    """
    app = adsk.core.Application.get()

    design = app.activeProduct

    data = []

    if not design:
        return data

    root = design.rootComponent

    for occ in root.occurrences:

        component = occ.component

        if component.bRepBodies.count == 0:
            continue

        body = component.bRepBodies.item(0)

        collision = detect_collision_shape(
            body
        )
        
        # Generate mesh filename based on component name
        mesh_filename = f"{component.name}.stl"

        data.append({

            "name": component.name,
            
            "mesh": mesh_filename,

            "collision": collision

        })

    return data