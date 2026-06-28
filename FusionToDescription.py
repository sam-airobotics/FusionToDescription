import adsk.core
import traceback

handlers = []

# def run(context):
#     app = adsk.core.Application.get()
#     ui = app.userInterface

#     ui.messageBox("FusionToDescription started")

#     from .commands import export_command
#     export_command.start()

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