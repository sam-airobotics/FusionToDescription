"""
Input changed handler for the export command.

Handles dynamic UI updates when user changes input values.
"""

import adsk.core
import traceback

from .helpers.input_utils import (
    get_bool_value,
    get_selected_item,
    set_visibility,
    set_numeric_value
)

from .ui import ui_context

from ..fusion.component_parser import get_component_data
from ..fusion.inertia_calculator import calculate_inertia


class InputChangedHandler(adsk.core.InputChangedEventHandler):
    """Handles input changed events for dynamic UI updates."""

    def __init__(self, app_ref, ui_ref):
        """Initialize with app and UI references.
        
        Args:
            app_ref: Callable that returns current app
            ui_ref: Callable that returns current UI
        """
        super().__init__()
        self.get_app = app_ref
        self.get_ui = ui_ref

    def notify(self, args):
        """Handle input changed event.
        
        Args:
            args: InputChangedEventArgs
        """
        try:
            ui = self.get_ui()
            if not ui:
                return

            changed_input = args.input
            inputs = args.inputs

            # Handle collision mode changes
            if changed_input.id == "collision_mode":
                self._handle_collision_mode_change(inputs)

            # Handle primitive mode changes
            elif changed_input.id == "primitive_mode":
                self._handle_primitive_mode_change(inputs)

            # Handle mass value changes (auto-calculate inertia)
            elif changed_input.id.endswith("_mass"):
                self._handle_mass_change(inputs, changed_input.id)

        except Exception as e:
            ui = self.get_ui()
            if ui:
                ui.messageBox(
                    f"Error processing input: {str(e)}\n\n{traceback.format_exc()}"
                )

    def _handle_collision_mode_change(self, inputs):
        """Handle collision mode radio button change.
        
        Args:
            inputs: Command inputs container
        """
        collision_mode_name = get_selected_item(inputs, "collision_mode")
        is_primitive = collision_mode_name == "primitive collision"

        primitive_group = ui_context.get_primitive_group()
        if primitive_group:
            primitive_group.isVisible = is_primitive

        set_visibility(inputs, "mesh_info", not is_primitive)

    def _handle_primitive_mode_change(self, inputs):
        """Handle primitive mode radio button change.
        
        Args:
            inputs: Command inputs container
        """
        primitive_mode_name = get_selected_item(inputs, "primitive_mode")
        show_manual = primitive_mode_name == "manual shapes"

        manual_shape_group = ui_context.get_manual_shape_group()
        if manual_shape_group:
            manual_shape_group.isVisible = show_manual

    def _handle_mass_change(self, inputs, mass_input_id):
        """Handle mass value change (auto-calculate inertia).
        
        Args:
            inputs: Command inputs container
            mass_input_id: ID of the mass input that changed
        """
        # Check if auto-inertia is enabled
        if not get_bool_value(inputs, "auto_inertia"):
            return

        # Extract component name from input ID
        link_name = mass_input_id.replace("_mass", "")

        # Get new mass value
        try:
            new_mass = inputs.itemById(mass_input_id).value
        except:
            return

        # Find component geometry
        components = get_component_data()
        collision = None
        shape = None

        for component in components:
            if component["name"] == link_name:
                collision = component.get("collision", {})
                shape = collision.get("shape", "Box")
                break

        if not collision:
            return

        # Calculate new inertia
        try:
            inertia = calculate_inertia(shape, new_mass, collision)

            # Update inertia inputs
            set_numeric_value(inputs, f"{link_name}_ixx", inertia["ixx"])
            set_numeric_value(inputs, f"{link_name}_iyy", inertia["iyy"])
            set_numeric_value(inputs, f"{link_name}_izz", inertia["izz"])

        except Exception as e:
            print(f"Error calculating inertia: {str(e)}")
