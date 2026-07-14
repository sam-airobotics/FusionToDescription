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


def clear_collision_groups():
    """
    Clear all stored collision group references.
    Call this when the command is destroyed.
    """
    collision_groups.clear()
