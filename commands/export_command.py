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
startup_splash_active = False
programmatic_launch_pending = False

cmd_def = None
control = None


class CommandStartingHandler(adsk.core.ApplicationCommandEventHandler):
    """Intercepts every user launch so the splash can run first."""

    def __init__(self):
        super().__init__()

    def notify(self, args):
        global startup_thread
        global startup_stop
        global startup_splash_active
        global programmatic_launch_pending

        try:
            event_args = adsk.core.ApplicationCommandEventArgs.cast(args)

            if event_args.commandId != config.COMMAND_ID:
                return

            # This is the second pass created by cmd_def.execute() after the
            # splash. Allow it to continue normally.
            if programmatic_launch_pending:
                programmatic_launch_pending = False
                return

            # Cancel the user's immediate launch. A custom event will launch
            # the same command again after the five-second splash.
            event_args.isCanceled = True

            # Do not start another timer if the splash is already active.
            if startup_splash_active:
                return

            startup_splash_active = True
            splash.show(ui)

            if startup_stop:
                startup_stop.set()

            startup_stop = threading.Event()
            startup_thread = threading.Thread(
                target=_wait_for_splash,
                name="FusionToDescriptionStartup",
                daemon=True,
            )
            startup_thread.start()

        except Exception:
            Logger.error(
                f"Failed to handle FusionToDescription command start: "
                f"{traceback.format_exc()}"
            )


class CommandTerminatedHandler(adsk.core.ApplicationCommandEventHandler):
    """Resets splash/launch state after every exporter command termination."""

    def __init__(self):
        super().__init__()

    def notify(self, args):
        global startup_splash_active
        global programmatic_launch_pending

        try:
            event_args = adsk.core.ApplicationCommandEventArgs.cast(args)

            if event_args.commandId != config.COMMAND_ID:
                return

            startup_splash_active = False
            programmatic_launch_pending = False
            splash.hide()

        except Exception:
            Logger.error(
                f"Failed to reset exporter command state: "
                f"{traceback.format_exc()}"
            )


class StartupSplashEventHandler(adsk.core.CustomEventHandler):
    """Starts the exporter command after the splash delay."""

    def __init__(self):
        super().__init__()

    def notify(self, args):
        global startup_splash_active
        global programmatic_launch_pending

        try:
            if not cmd_def or not cmd_def.isValid:
                startup_splash_active = False
                splash.hide()
                return

            # The next commandStarting event belongs to this programmatic
            # launch, so it must not be canceled or start another splash.
            programmatic_launch_pending = True

            if not cmd_def.execute():
                programmatic_launch_pending = False
                startup_splash_active = False
                splash.hide()
                Logger.error("FusionToDescription command execution was rejected.")

        except Exception:
            programmatic_launch_pending = False
            startup_splash_active = False
            splash.hide()
            Logger.error(
                f"Failed to open export dialog after splash: "
                f"{traceback.format_exc()}"
            )


def _init_fusion_ui():
    """Initialize Fusion app and UI references."""
    global app, ui

    if app is None or ui is None:
        app = adsk.core.Application.get()
        if app:
            ui = app.userInterface

    return app, ui


def _wait_for_splash():
    """Wait without blocking Fusion, then queue the command on Fusion's main thread."""
    try:
        if startup_stop and startup_stop.wait(STARTUP_SPLASH_DELAY):
            return

        if app:
            app.fireCustomEvent(STARTUP_SPLASH_EVENT)

    except Exception:
        Logger.error(
            f"Startup splash sequence failed: {traceback.format_exc()}"
        )


def start():
    """Register the export command and recurring splash behavior."""
    global cmd_def, control, startup_event

    app, ui = _init_fusion_ui()
    if not ui:
        return

    try:
        # Custom events safely return control from the worker thread to Fusion's
        # main thread.
        startup_event = app.registerCustomEvent(STARTUP_SPLASH_EVENT)
        if startup_event:
            startup_handler = StartupSplashEventHandler()
            startup_event.add(startup_handler)
            handlers.append(startup_handler)

        icon_folder = os.path.join(
            os.path.dirname(__file__),
            "..",
            "resources",
            "icons"
        )

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

        # Intercept every user invocation from the toolbar button or dropdown.
        command_starting_handler = CommandStartingHandler()
        ui.commandStarting.add(command_starting_handler)
        handlers.append(command_starting_handler)

        # Explicitly reset state after the exporter closes, regardless of
        # whether the user clicks OK, Cancel, or another command terminates it.
        command_terminated_handler = CommandTerminatedHandler()
        ui.commandTerminated.add(command_terminated_handler)
        handlers.append(command_terminated_handler)

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
    global startup_splash_active, programmatic_launch_pending

    try:
        if startup_stop:
            startup_stop.set()

        startup_splash_active = False
        programmatic_launch_pending = False

        if app and startup_event:
            try:
                app.unregisterCustomEvent(STARTUP_SPLASH_EVENT)
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
