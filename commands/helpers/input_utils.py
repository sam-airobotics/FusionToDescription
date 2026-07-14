"""
Utilities for reading and writing input values.
"""


def get_string_value(inputs, input_id):
    """Get string value from input by ID."""
    try:
        return inputs.itemById(input_id).value.strip()
    except:
        return ""


def get_bool_value(inputs, input_id):
    """Get boolean value from input by ID."""
    try:
        return inputs.itemById(input_id).value
    except:
        return False


def get_numeric_value(inputs, input_id):
    """Get numeric value from input by ID."""
    try:
        return inputs.itemById(input_id).value
    except:
        return 0.0


def get_selected_item(inputs, input_id):
    """Get selected item name from radio/dropdown by ID."""
    try:
        return inputs.itemById(input_id).selectedItem.name.lower()
    except:
        return ""


def get_selected_name(inputs, input_id):
    """Return the selected item exactly as displayed."""

    try:
        return inputs.itemById(input_id).selectedItem.name
    except:
        return ""


def set_visibility(inputs, input_id, visible):
    """Set visibility of an input."""
    try:
        input_obj = inputs.itemById(input_id)
        if input_obj is not None:
            input_obj.isVisible = visible
    except:
        pass


def set_numeric_value(inputs, input_id, value):
    """Set numeric value of an input."""
    try:
        input_obj = inputs.itemById(input_id)
        if input_obj is not None:
            input_obj.value = value
    except:
        pass

def get_input(inputs, input_id):
    """Return an input object by ID."""
    try:
        return inputs.itemById(input_id)
    except:
        return None


def set_text_value(inputs, input_id, text):
    """Update the text of a TextBoxCommandInput."""
    try:
        input_obj = inputs.itemById(input_id)
        if input_obj is not None:
            input_obj.text = text
    except:
        pass
