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
# Material Colors
# =========================================================
   
material_color_inputs = {}
    
def register_material_color(component_name, color_input):
    """
    Register the color picker for a component.
    """
    material_color_inputs[component_name] = color_input
    

def get_material_color(component_name):
    """
    Get the ColorCommandInput for a component.
    """
    return material_color_inputs.get(component_name)


def get_all_material_colors():
    """
    Return dictionary of all registered color inputs.
    """
    return material_color_inputs


def clear_material_colors():
    """
    Clear material input cache when command closes.
    """
    material_color_inputs.clear()