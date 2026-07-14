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
