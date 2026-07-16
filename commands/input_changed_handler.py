"""
Input changed handler for the export command.

Handles dynamic UI updates when user changes input values.
"""

import adsk.core
import traceback

from .helpers.input_utils import (
    get_bool_value,
    get_selected_item,
    get_selected_name,
    set_visibility,
    set_numeric_value
)

from .ui import ui_context

from ..fusion.inertia_calculator import calculate_inertia

from ..fusion.collision_detector import build_collision

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

            elif changed_input.id.endswith("_collision"):
                self._handle_collision_shape_change(inputs, changed_input)

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

        component = ui_context.get_component(link_name)

        if component is None:
            return
        
        collision = component["collision"]

        print(f"Updated cache: {component_name}")
        print(component["collision"])
        
        shape = collision["shape"]

        # Calculate new inertia
        try:
            inertia = calculate_inertia(shape, new_mass, collision)

            # Update inertia inputs
            set_numeric_value(inputs, f"{link_name}_ixx", inertia["ixx"])
            set_numeric_value(inputs, f"{link_name}_iyy", inertia["iyy"])
            set_numeric_value(inputs, f"{link_name}_izz", inertia["izz"])

        except Exception as e:
            print(f"Error calculating inertia: {str(e)}")

    def _handle_collision_shape_change(self, inputs, changed_input):
        """Handle collision shape dropdown changes."""
        
        from .ui.simulation_tab import refresh_collision_info
        
        component_name = changed_input.id.replace("_collision", "")
        selected_shape = changed_input.selectedItem.name
    
        # Retrieve the cached component
        component = ui_context.get_component(component_name)
    
        if component is None:
            return
    
        # Build the new collision geometry from the stored dimensions
        collision = build_collision(
            component["dimensions"],
            selected_shape
        )
    
        # Update the cached collision data
        component["collision"] = collision

        if get_bool_value(inputs, "auto_inertia"):
        
            try:
        
                mass_input = inputs.itemById(f"{component_name}_mass")
        
                if mass_input:
        
                    inertia = calculate_inertia(
                        collision["shape"],
                        mass_input.value,
                        collision
                    )
        
                    set_numeric_value(
                        inputs,
                        f"{component_name}_ixx",
                        inertia["ixx"]
                    )
        
                    set_numeric_value(
                        inputs,
                        f"{component_name}_iyy",
                        inertia["iyy"]
                    )
        
                    set_numeric_value(
                        inputs,
                        f"{component_name}_izz",
                        inertia["izz"]
                    )
        
            except Exception:
                pass
        
        # Refresh the UI
        refresh_collision_info(
            component_name,
            collision
        )
