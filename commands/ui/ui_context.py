"""
Shared UI context and state management.

This module maintains references to dynamically updated UI elements
that need to be modified by input change handlers.
"""

# Global UI element references that are updated dynamically
primitive_group = None
manual_shape_group = None


def set_primitive_group(group):
    """Store reference to primitive collision group."""
    global primitive_group
    primitive_group = group


def get_primitive_group():
    """Get reference to primitive collision group."""
    return primitive_group


def set_manual_shape_group(group):
    """Store reference to manual shape group."""
    global manual_shape_group
    manual_shape_group = group


def get_manual_shape_group():
    """Get reference to manual shape group."""
    return manual_shape_group


# =========================================================
# Material Visualization Dropdowns
# =========================================================

material_dropdowns = {}


def register_material_dropdown(component_name, dropdown):
    """
    Register the visualization color dropdown for a component.
    """
    material_dropdowns[component_name] = dropdown


def get_material_dropdown(component_name):
    """
    Get the visualization color dropdown for a component.
    """
    return material_dropdowns.get(component_name)


def get_all_material_dropdowns():
    """
    Return all registered visualization color dropdowns.
    """
    return material_dropdowns


def clear_material_dropdowns():
    """
    Clear dropdown cache when the command closes.
    """
    material_dropdowns.clear()
