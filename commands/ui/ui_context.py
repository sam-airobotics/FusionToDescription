"""
Shared UI context and state management.

This module maintains references to dynamically updated UI elements
that need to be modified by input change handlers.
"""

# ------------------------------------------------------------------
# Global UI element references
# ------------------------------------------------------------------

primitive_group = None
manual_shape_group = None

# Stores collision info groups for each component
collision_groups = {}

# Stores parsed component data
component_data = {}
# ------------------------------------------------------------------
# Primitive Collision Group
# ------------------------------------------------------------------

def set_primitive_group(group):
    """Store reference to primitive collision group."""
    global primitive_group
    primitive_group = group


def get_primitive_group():
    """Get reference to primitive collision group."""
    return primitive_group


# ------------------------------------------------------------------
# Manual Shape Group
# ------------------------------------------------------------------

def set_manual_shape_group(group):
    """Store reference to manual shape group."""
    global manual_shape_group
    manual_shape_group = group


def get_manual_shape_group():
    """Get reference to manual shape group."""
    return manual_shape_group


# ------------------------------------------------------------------
# Collision Info Groups
# ------------------------------------------------------------------

def register_collision_group(component_name, group):
    """
    Store the collision info group for a component.

    Args:
        component_name: Component/link name
        group: GroupCommandInput
    """
    collision_groups[component_name] = group


def get_collision_group(component_name):
    """
    Get the collision info group for a component.

    Args:
        component_name: Component/link name

    Returns:
        GroupCommandInput or None
    """
    return collision_groups.get(component_name)

# ------------------------------------------------------------------
# Component Data
# ------------------------------------------------------------------

def set_component_data(components):
    """Store parsed component data."""

    component_data.clear()

    for component in components:
        component_data[component["name"]] = component


def get_component(component_name):
    """
    Get a component by name.

    Args:
        component_name: Component name

    Returns:
        Component dictionary or None
    """
    return component_data.get(component_name)


def get_all_components():
    """
    Return all cached components.
    """
    return list(component_data.values())

def clear():
    """Clear all cached UI state."""

    global primitive_group
    global manual_shape_group

    primitive_group = None
    manual_shape_group = None

    collision_groups.clear()
    component_data.clear()
