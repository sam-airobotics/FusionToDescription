"""FusionToDescription Autodesk Fusion 360 add-in entry point.

Version: 0.1.3
"""

import adsk.core
import traceback

__version__ = "0.1.3"

handlers = []


def run(context):
    try:
        from .commands import export_command
        export_command.start()

    except Exception as e:
        app = adsk.core.Application.get()
        if app:
            ui = app.userInterface
            ui.messageBox(
                f"Error starting add-in: {str(e)}\n\n{traceback.format_exc()}"
            )


def stop(context):
    try:
        from .commands import export_command
        export_command.stop()

    except Exception as e:
        app = adsk.core.Application.get()
        if app:
            ui = app.userInterface
            ui.messageBox(
                f"Error stopping add-in: {str(e)}\n\n{traceback.format_exc()}"
            )
