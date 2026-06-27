"""
UI building utilities for creating common UI elements.
"""

import adsk.core


def create_radio_group(parent, group_id, group_name, items):
    """Create a radio button group with items.
    
    Args:
        parent: Parent UI container
        group_id: Unique ID for the group
        group_name: Display name for the group
        items: List of (name, is_selected) tuples
        
    Returns:
        The created RadioButtonGroupCommandInput
    """
    group = parent.addRadioButtonGroupCommandInput(group_id)
    for name, is_selected in items:
        group.listItems.add(name, is_selected, "")
    return group


def create_bool_input(parent, input_id, label, checked=True):
    """Create a boolean value input.
    
    Args:
        parent: Parent UI container
        input_id: Unique ID
        label: Display label
        checked: Default state
        
    Returns:
        The created BoolValueCommandInput
    """
    return parent.addBoolValueInput(
        input_id,
        label,
        True,
        "",
        checked
    )


def create_string_input(parent, input_id, label, value=""):
    """Create a string value input.
    
    Args:
        parent: Parent UI container
        input_id: Unique ID
        label: Display label
        value: Default value
        
    Returns:
        The created StringValueCommandInput
    """
    return parent.addStringValueInput(input_id, label, value)


def create_value_input(parent, input_id, label, unit, value):
    """Create a numeric value input.
    
    Args:
        parent: Parent UI container
        input_id: Unique ID
        label: Display label
        unit: Unit string (e.g., "kg", "m")
        value: Numeric default value
        
    Returns:
        The created ValueCommandInput
    """
    return parent.addValueInput(
        input_id,
        label,
        unit,
        adsk.core.ValueInput.createByReal(value)
    )


def create_text_box(parent, input_id, label, content, rows=1, read_only=True):
    """Create a text box input.
    
    Args:
        parent: Parent UI container
        input_id: Unique ID
        label: Display label
        content: Initial text content
        rows: Number of rows
        read_only: Whether text box is read-only
        
    Returns:
        The created TextBoxCommandInput
    """
    return parent.addTextBoxCommandInput(
        input_id,
        label,
        content,
        rows,
        read_only
    )


def create_dropdown(parent, input_id, label, items, selected_index=0):
    """Create a dropdown menu.
    
    Args:
        parent: Parent UI container
        input_id: Unique ID
        label: Display label
        items: List of item names
        selected_index: Index of selected item
        
    Returns:
        The created DropDownCommandInput
    """
    dropdown = parent.addDropDownCommandInput(
        input_id,
        label,
        adsk.core.DropDownStyles.TextListDropDownStyle
    )
    for i, item in enumerate(items):
        dropdown.listItems.add(item, i == selected_index, "")
    return dropdown


def create_group(parent, group_id, group_name):
    """Create a group container.
    
    Args:
        parent: Parent UI container
        group_id: Unique ID
        group_name: Display name
        
    Returns:
        The created GroupCommandInput
    """
    return parent.addGroupCommandInput(group_id, group_name)


def create_tab(parent, tab_id, tab_name):
    """Create a tab container.
    
    Args:
        parent: Parent UI container (usually commandInputs)
        tab_id: Unique ID
        tab_name: Display name
        
    Returns:
        The created TabCommandInput
    """
    return parent.addTabCommandInput(tab_id, tab_name)
