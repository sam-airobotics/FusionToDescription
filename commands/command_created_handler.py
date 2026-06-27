"""
Command created handler for the export command.

Builds the complete dialog UI when the command is first created.
"""

import adsk.core
import traceback

from .ui.general_tab import build_general_tab
from .ui.properties_tab import build_properties_tab
from .ui.simulation_tab import build_simulation_tab
from .ui.advanced_tab import build_advanced_tab

from .execute_handler import ExecuteHandler
from .input_changed_handler import InputChangedHandler


class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    """Handles the command created event to build the dialog UI."""

    def __init__(self, app_ref, ui_ref, handlers_list):
        """Initialize with app, UI, and handlers list references.
        
        Args:
            app_ref: Callable that returns current app
            ui_ref: Callable that returns current UI
            handlers_list: List to store event handler references
        """
        super().__init__()
        self.get_app = app_ref
        self.get_ui = ui_ref
        self.handlers_list = handlers_list

    def notify(self, args):
        """Handle command created event.
        
        Args:
            args: CommandCreatedEventArgs
        """
        try:
            ui = self.get_ui()
            if not ui:
                return

            cmd = args.command

            # Set dialog size
            cmd.setDialogInitialSize(500, 250)

            inputs = cmd.commandInputs

            # Build all tabs
            build_general_tab(inputs)
            build_properties_tab(inputs)
            build_simulation_tab(inputs)
            build_advanced_tab(inputs)

            # Attach execute handler
            execute_handler = ExecuteHandler(self.get_app, self.get_ui)
            cmd.execute.add(execute_handler)
            self.handlers_list.append(execute_handler)

            # Attach input changed handler
            input_changed_handler = InputChangedHandler(self.get_app, self.get_ui)
            cmd.inputChanged.add(input_changed_handler)
            self.handlers_list.append(input_changed_handler)

        except Exception as e:
            ui = self.get_ui()
            if ui:
                ui.messageBox(
                    f"Error creating command UI: {str(e)}\n\n{traceback.format_exc()}"
                )
