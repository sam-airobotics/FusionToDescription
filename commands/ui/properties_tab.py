"""
Properties tab for the export dialog.

Includes mass properties and inertia tensor configuration.
"""

import adsk.core

from ..helpers.ui_builder import (
    create_bool_input,
    create_group,
    create_text_box,
    create_value_input
)

from ...fusion.mass_extractor import get_mass_data
from ...fusion.component_parser import get_component_data
from ...fusion.inertia_calculator import calculate_inertia


def build_properties_tab(inputs):
    """Build the Properties tab UI.
    
    Args:
        inputs: The command's commandInputs container
        
    Returns:
        The created TabCommandInput
    """
    properties_tab = inputs.addTabCommandInput(
        "properties_tab",
        "Properties"
    )

    properties_inputs = properties_tab.children

    # Mass Properties Group
    mass_group = create_group(
        properties_inputs,
        "mass_group",
        "Mass Properties"
    )

    mass_group_inputs = mass_group.children

    create_bool_input(
        mass_group_inputs,
        "use_physical_properties",
        "Use Fusion Physical Properties",
        True
    )

    # Add mass inputs for each component
    mass_data = get_mass_data()

    for link in mass_data:
        create_value_input(
            mass_group_inputs,
            f"{link['name']}_mass",
            f"{link['name']} Mass",
            "kg",
            link["mass"]
        )

    # Inertia Properties Group
    inertia_group = create_group(
        properties_inputs,
        "inertia_group",
        "Inertia Properties"
    )

    inertia_inputs = inertia_group.children

    # Auto-calculate inertia checkbox
    create_bool_input(
        inertia_inputs,
        "auto_inertia",
        "Auto Calculate From Shape",
        True
    )

    # Build mass lookup table
    mass_lookup = {item["name"]: item["mass"] for item in mass_data}

    # Get component geometry
    components = get_component_data()

    # Create inertia entries for each component
    for component in components:
        _build_component_inertia_group(
            inertia_inputs,
            component,
            mass_lookup
        )

    return properties_tab


def _build_component_inertia_group(parent, component, mass_lookup):
    """Build inertia group for a single component.
    
    Args:
        parent: Parent UI container
        component: Component data dict
        mass_lookup: Dict mapping component names to masses
    """
    name = component["name"]

    collision = component.get("collision", {})
    shape = collision.get("shape", "Box")

    mass = mass_lookup.get(name, 1.0)

    # Calculate inertia
    try:
        inertia = calculate_inertia(shape, mass, collision)
    except:
        inertia = {"ixx": 0.0, "iyy": 0.0, "izz": 0.0}

    # Create group for this component
    group = create_group(
        parent,
        f"{name}_inertia_group",
        f"{name} Inertia"
    )

    group_inputs = group.children

    # Display detected shape
    create_text_box(
        group_inputs,
        f"{name}_shape_display",
        "Shape",
        shape,
        1,
        True
    )

    # Inertia components
    create_value_input(
        group_inputs,
        f"{name}_ixx",
        "Ixx",
        "kg*m^2",
        inertia["ixx"]
    )

    create_value_input(
        group_inputs,
        f"{name}_iyy",
        "Iyy",
        "kg*m^2",
        inertia["iyy"]
    )

    create_value_input(
        group_inputs,
        f"{name}_izz",
        "Izz",
        "kg*m^2",
        inertia["izz"]
    )

    # Off-diagonal terms (usually zero)
    create_value_input(
        group_inputs,
        f"{name}_ixy",
        "Ixy",
        "kg*m^2",
        0.0
    )

    create_value_input(
        group_inputs,
        f"{name}_ixz",
        "Ixz",
        "kg*m^2",
        0.0
    )

    create_value_input(
        group_inputs,
        f"{name}_iyz",
        "Iyz",
        "kg*m^2",
        0.0
    )
