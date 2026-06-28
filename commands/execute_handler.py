"""
Execute handler for the export command.

Handles when the user clicks the export/OK button.
"""

import adsk.core
import traceback

from .helpers.input_utils import (
    get_string_value,
    get_bool_value,
    get_selected_item
)

from ..exporter.export_config import ExportConfig
from ..exporter.export_manager import ExportManager
from ..utils.validate import Validator
from ..utils.logger import Logger


class ExecuteHandler(adsk.core.CommandEventHandler):
    """Handles the execute event when exporting."""

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
        """Handle execute event.
        
        Args:
            args: CommandEventArgs
        """
        try:
            ui = self.get_ui()
            if not ui:
                return

            command = args.firingEvent.sender
            inputs = command.commandInputs

            # Read input values
            robot_name = get_string_value(inputs, "robot_name")
            export_directory = get_string_value(inputs, "export_path")
            ros_distro = get_selected_item(inputs, "ros_distro")
            generate_launch = get_bool_value(inputs, "generate_launch")
            generate_rviz = get_bool_value(inputs, "generate_rviz")
            generate_gazebo = get_bool_value(inputs, "generate_gazebo")
            generate_control = get_bool_value(inputs, "generate_control")

            # Create export configuration
            export_config = ExportConfig(
                robot_name=robot_name,
                export_directory=export_directory,
                ros_distro=ros_distro,
                generate_launch=generate_launch,
                generate_rviz=generate_rviz,
                generate_gazebo=generate_gazebo,
                generate_ros2_control=generate_control
            )

            # Validate configuration
            validator = Validator(export_config)
            result = validator.validate()

            if not result["valid"]:
                ui.messageBox("\n".join(result["errors"]))
                return

            # Run export
            manager = ExportManager(export_config)
            manager.export()

            ui.messageBox("Export completed successfully.")

        except Exception as e:
            ui = self.get_ui()
            if ui:
                ui.messageBox(
                    f"Export Error: {str(e)}\n\n{traceback.format_exc()}"
                )
