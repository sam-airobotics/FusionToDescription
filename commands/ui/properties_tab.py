"""
Properties tab for the export dialog.

Includes mass properties, inertia tensor configuration,
and material visualization settings.
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
from ...fusion.material_parser import MaterialParser

from . import ui_context


def build_properties_tab(inputs):
    """
    Build the Properties tab UI.

    Args:
        inputs: CommandInputs container

    Returns:
        Created TabCommandInput
    """

    properties_tab = inputs.addTabCommandInput(
        "properties_tab",
        "Properties"
    )

    properties_inputs = properties_tab.children

    # =====================================================
    # Mass Properties
    # =====================================================

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

    mass_data = get_mass_data()

    for link in mass_data:

        create_value_input(
            mass_group_inputs,
            f"{link['name']}_mass",
            f"{link['name']} Mass",
            "kg",
            link["mass"]
        )

    # =====================================================
    # Inertia Properties
    # =====================================================

    inertia_group = create_group(
        properties_inputs,
        "inertia_group",
        "Inertia Properties"
    )

    inertia_inputs = inertia_group.children

    create_bool_input(
        inertia_inputs,
        "auto_inertia",
        "Auto Calculate From Shape",
        True
    )

    mass_lookup = {
        item["name"]: item["mass"]
        for item in mass_data
    }

    components = get_component_data()

    for component in components:

        _build_component_inertia_group(
            inertia_inputs,
            component,
            mass_lookup
        )

    # =====================================================
    # Material Properties
    # =====================================================

    material_group = create_group(
        properties_inputs,
        "material_group",
        "Material Properties"
    )

    material_inputs = material_group.children

    create_text_box(
        material_inputs,
        "material_info",
        "",
        "Fusion material names are preserved. "
        "Choose the visualization color used in RViz and Gazebo.",
        2,
        True
    )

    parser = MaterialParser()

    materials = parser.parse()

    visualization_colors = [
        "Default",
        "White",
        "Black",
        "Gray",
        "Silver",
        "Red",
        "Green",
        "Blue",
        "Yellow",
        "Orange",
        "Purple"
    ]

    for component_name, material in materials.items():

        # ---------------------------------------------
        # Fusion Material Name (Read Only)
        # ---------------------------------------------

        create_text_box(
            material_inputs,
            f"{component_name}_material",
            component_name,
            material.name,
            1,
            True
        )

        # ---------------------------------------------
        # Visualization Color
        # ---------------------------------------------

        dropdown = material_inputs.addDropDownCommandInput(
            f"{component_name}_color",
            f"{component_name} Color",
            adsk.core.DropDownStyles.TextListDropDownStyle
        )

        for color in visualization_colors:

            dropdown.listItems.add(
                color,
                color == "Default"
            )

        ui_context.register_material_dropdown(
            component_name,
            dropdown
        )
        
    return properties_tab


def _build_component_inertia_group(
    parent,
    component,
    mass_lookup
):
    """
    Build inertia controls for one component.
    """

    name = component["name"]

    collision = component.get(
        "collision",
        {}
    )

    shape = collision.get(
        "shape",
        "Box"
    )

    mass = mass_lookup.get(
        name,
        1.0
    )

    try:

        inertia = calculate_inertia(
            shape,
            mass,
            collision
        )

    except Exception:

        inertia = {
            "ixx": 0.0,
            "iyy": 0.0,
            "izz": 0.0
        }

    group = create_group(
        parent,
        f"{name}_inertia_group",
        f"{name} Inertia"
    )

    group_inputs = group.children

    create_text_box(
        group_inputs,
        f"{name}_shape_display",
        "Shape",
        shape,
        1,
        True
    )

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
