"""
Simulation tab for the export dialog.

Includes collision generation, Gazebo, and ros2_control settings.
"""

import adsk.core

from ..helpers.ui_builder import (
    create_bool_input,
    create_group,
    create_text_box,
    create_radio_group,
    create_dropdown
)

from . import ui_context

from ...fusion.component_parser import get_component_data


def build_simulation_tab(inputs):
    """Build the Simulation tab UI.
    
    Args:
        inputs: The command's commandInputs container
        
    Returns:
        The created TabCommandInput
    """
    simulation_tab = inputs.addTabCommandInput(
        "simulation_tab",
        "Simulation"
    )

    simulation_inputs = simulation_tab.children

    # Collision generation settings
    _build_collision_group(simulation_inputs)

    # Manual shape assignment group
    _build_manual_shapes_group(simulation_inputs)

    # Gazebo settings
    gazebo_group = create_group(
        simulation_inputs,
        "gazebo_group",
        "Gazebo"
    )

    gazebo_inputs = gazebo_group.children

    create_bool_input(
        gazebo_inputs,
        "generate_gazebo_plugins",
        "Generate Gazebo Plugins",
        True
    )

    # ros2_control settings
    control_group = create_group(
        simulation_inputs,
        "control_group",
        "ros2_control"
    )

    control_inputs = control_group.children

    create_bool_input(
        control_inputs,
        "generate_controller_yaml",
        "Generate controllers.yaml",
        True
    )

    return simulation_tab


def _build_collision_group(parent):
    """Build collision generation settings group."""
    collision_group = create_group(
        parent,
        "collision_group",
        "Collision Generation"
    )

    collision_group_inputs = collision_group.children

    # Collision mode selection
    create_radio_group(
        collision_group_inputs,
        "collision_mode",
        "Collision Mode",
        [
            ("Primitive Collision", True),
            ("Mesh Collision", False),
        ]
    )

    # Mesh info (visible when Mesh Collision is selected)
    mesh_info = create_text_box(
        collision_group_inputs,
        "mesh_info",
        "Info",
        "Collision geometry will be generated from exported STL meshes.",
        2,
        True
    )
    mesh_info.isVisible = False

    # Primitive collision options
    primitive_group = create_group(
        collision_group_inputs,
        "primitive_group",
        "Primitive Collision Mode"
    )

    ui_context.set_primitive_group(primitive_group)

    primitive_inputs = primitive_group.children

    create_radio_group(
        primitive_inputs,
        "primitive_mode",
        "Primitive Mode",
        [
            ("Auto Detect", True),
            ("Manual Shapes", False),
        ]
    )


def _build_manual_shapes_group(parent):
    """Build manual shape assignment group."""
    manual_shape_group = create_group(
        parent,
        "manual_shape_group",
        "Link Collision Assignment"
    )

    manual_shape_group.isVisible = False

    ui_context.set_manual_shape_group(manual_shape_group)

    manual_inputs = manual_shape_group.children

    # Get components
    components = get_component_data()

    if not components:
        create_text_box(
            manual_inputs,
            "no_components",
            "Info",
            "No Fusion Components Found",
            1,
            True
        )
    else:
        for component in components:
            _build_component_collision_entry(manual_inputs, component)


def _build_component_collision_entry(parent, component):
    """Build collision settings for a single component.
    
    Args:
        parent: Parent UI container
        component: Component data dict
    """
    name = component["name"]

    collision = component.get("collision", {})
    shape = collision.get("shape", "Box")

    # Shape dropdown
    create_dropdown(
        parent,
        f"{name}_collision",
        name,
        ["Box", "Cylinder", "Sphere"],
        {"Box": 0, "Cylinder": 1, "Sphere": 2}.get(shape, 0)
    )

    # Collision info group
    info_group = create_group(
        parent,
        f"{name}_collision_info",
        f"{name} Collision"
    )

    info_inputs = info_group.children

    # Detected shape display
    create_text_box(
        info_inputs,
        f"{name}_shape",
        "Detected Shape",
        shape,
        1,
        True
    )

    # Display collision parameters based on shape
    if shape == "Box":
        create_text_box(
            info_inputs,
            f"{name}_length",
            "Length (m)",
            str(round(collision.get("length", 0.0), 4)),
            1,
            True
        )

        create_text_box(
            info_inputs,
            f"{name}_breadth",
            "Breadth (m)",
            str(round(collision.get("breadth", 0.0), 4)),
            1,
            True
        )

        create_text_box(
            info_inputs,
            f"{name}_height",
            "Height (m)",
            str(round(collision.get("height", 0.0), 4)),
            1,
            True
        )

    elif shape == "Cylinder":
        create_text_box(
            info_inputs,
            f"{name}_radius",
            "Radius (m)",
            str(round(collision.get("radius", 0.0), 4)),
            1,
            True
        )

        create_text_box(
            info_inputs,
            f"{name}_height",
            "Height (m)",
            str(round(collision.get("height", 0.0), 4)),
            1,
            True
        )

    elif shape == "Sphere":
        create_text_box(
            info_inputs,
            f"{name}_radius",
            "Radius (m)",
            str(round(collision.get("radius", 0.0), 4)),
            1,
            True
        )
