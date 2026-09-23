"""
export_command.py

Entry point for the export command.
Handles registration and lifecycle of the export UI command.
"""

import os
import threading
import adsk.core
import traceback

from .. import config
from ..utils.logger import Logger

from .command_created_handler import CommandCreatedHandler
from .ui import splash


STARTUP_SPLASH_EVENT = "FusionToDescriptionStartupSplashFinished"
STARTUP_SPLASH_DELAY = 5.0


# Global state
app = None
ui = None

handlers = []
startup_thread = None
startup_stop = None
startup_event = None

cmd_def = None
control = None


class StartupSplashEventHandler(adsk.core.CustomEventHandler):
    """Opens the FusionToDescription dialog after the splash delay."""

    def __init__(self):
        super().__init__()

    def notify(self, args):
        global startup_event

        try:
            splash.hide()

            if cmd_def and cmd_def.isValid:
                cmd_def.execute()
        except Exception:
            Logger.error(
                f"Failed to open export dialog after splash: {traceback.format_exc()}"
            )


def _init_fusion_ui():
    """Initialize Fusion app and UI references."""
    global app, ui

    if app is None or ui is None:
        app = adsk.core.Application.get()
        if app:
            ui = app.userInterface

    return app, ui


def _start_splash_sequence():
    """Keep the splash visible for five seconds, then return to Fusion's main thread."""
    try:
        if startup_stop.wait(STARTUP_SPLASH_DELAY):
            return

        if app:
            app.fireCustomEvent(STARTUP_SPLASH_EVENT)
    except Exception:
        Logger.error(
            f"Startup splash sequence failed: {traceback.format_exc()}"
        )


def start():
    """Start the export command and show the startup logo for five seconds."""
    global cmd_def, control, startup_event, startup_thread, startup_stop

    app, ui = _init_fusion_ui()
    if not ui:
        return

    try:
        # Display the centered logo immediately.
        splash.show(ui)

        # Register an event so the command dialog is opened safely on
        # Fusion's main thread after the five-second delay.
        startup_event = app.registerCustomEvent(STARTUP_SPLASH_EVENT)
        if startup_event:
            startup_handler = StartupSplashEventHandler()
            startup_event.add(startup_handler)
            handlers.append(startup_handler)

        startup_stop = threading.Event()
        startup_thread = threading.Thread(
            target=_start_splash_sequence,
            name="FusionToDescriptionStartup",
            daemon=True,
        )
        startup_thread.start()

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

        def get_ui_ref():
            return _init_fusion_ui()[1]

        on_created = CommandCreatedHandler(
            _init_fusion_ui,
            get_ui_ref,
            handlers
        )

        cmd_def.commandCreated.add(on_created)
        handlers.append(on_created)

        panel = ui.allToolbarPanels.itemById(config.PANEL_ID)

        if panel is None:
            ui.messageBox(f"Panel not found: {config.PANEL_ID}")
            return

        control = panel.controls.addCommand(cmd_def)

        Logger.info(
            f"Export command '{config.COMMAND_NAME}' registered successfully"
        )

    except Exception as e:
        Logger.error(f"Failed to start export command: {str(e)}")
        splash.stop()

        if ui:
            ui.messageBox(
                f"Error starting add-in: {str(e)}\n\n{traceback.format_exc()}"
            )


def stop():
    """Stop the export command and clean up startup resources."""
    global control, cmd_def, startup_event, startup_thread, startup_stop

    try:
        if startup_stop:
            startup_stop.set()

        if startup_event and startup_event.isValid:
            try:
                startup_event.deleteMe()
            except Exception:
                pass

        splash.stop()

        if control:
            control.deleteMe()
            control = None

        if cmd_def:
            cmd_def.deleteMe()
            cmd_def = None

        startup_thread = None
        startup_stop = None
        startup_event = None

        Logger.info("Export command stopped successfully")

    except Exception as e:
        Logger.error(f"Error stopping command: {str(e)}")
