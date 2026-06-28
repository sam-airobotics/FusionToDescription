"""
export_command.py

Entry point for the export command.
Handles registration and lifecycle of the export UI command.
"""

import os
import adsk.core
import traceback

from .. import config
from ..utils.logger import Logger

from .command_created_handler import CommandCreatedHandler


# Global state
app = None
ui = None

handlers = []

cmd_def = None
control = None


def _init_fusion_ui():
    """Initialize Fusion app and UI references.
    
    Returns:
        Tuple of (app, ui) or (None, None) if unavailable
    """
    global app, ui
    if app is None or ui is None:
        app = adsk.core.Application.get()
        if app:
            ui = app.userInterface
    return app, ui


def start():
    """Start the export command.
    
    Creates the command button and registers event handlers.
    """
    global cmd_def, control

    app, ui = _init_fusion_ui()
    if not ui:
        return

    try:
        # Get icon folder
        icon_folder = os.path.join(
            os.path.dirname(__file__),
            "..",
            "resources",
            "icons"
        )

        # Create command definition
        cmd_def = ui.commandDefinitions.addButtonDefinition(
            config.COMMAND_ID,
            config.COMMAND_NAME,
            "Fusion 360 to ROS2 Description Package Exporter",
            icon_folder
        )

        # Create and attach command created handler
        def get_ui_ref():
            """Closure to get current UI reference."""
            return _init_fusion_ui()[1]

        on_created = CommandCreatedHandler(_init_fusion_ui, get_ui_ref, handlers)

        cmd_def.commandCreated.add(on_created)
        handlers.append(on_created)

        # Add command to toolbar
        # panel = ui.allToolbarPanels.itemById(config.PANEL_ID)
        # control = panel.controls.addCommand(cmd_def)

        panel = ui.allToolbarPanels.itemById(config.PANEL_ID)

        if panel is None:
            ui.messageBox(f"Panel not found: {config.PANEL_ID}")

            panels = ui.allToolbarPanels
            ids = []
            for i in range(panels.count):
                ids.append(panels.item(i).id)

            ui.messageBox("\n".join(ids))
            return

        control = panel.controls.addCommand(cmd_def)
        control.isPromoted = True

        Logger.info(f"Export command '{config.COMMAND_NAME}' registered successfully")

    except Exception as e:
        Logger.error(f"Failed to start export command: {str(e)}")
        if ui:
            ui.messageBox(
                f"Error starting add-in: {str(e)}\n\n{traceback.format_exc()}"
            )


def stop():
    """Stop the export command.
    
    Removes the command button and cleans up handlers.
    """
    global control, cmd_def

    try:
        if control:
            control.deleteMe()
            control = None

        if cmd_def:
            cmd_def.deleteMe()
            cmd_def = None

        Logger.info("Export command stopped successfully")

    except Exception as e:
        Logger.error(f"Error stopping command: {str(e)}")
