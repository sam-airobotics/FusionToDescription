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


class ExecuteHandler(adsk.core.CommandEventHandler):
    """Handles the execute event when exporting."""

    def __init__(self, app_ref, ui_ref):
        super().__init__()
        self.get_app = app_ref
        self.get_ui = ui_ref

    def notify(self, args):
        ui = None
        try:
            ui = self.get_ui()
            if not ui:
                return

            command = args.firingEvent.sender
            inputs = command.commandInputs

            robot_name = get_string_value(inputs, "robot_name")
            export_directory = get_string_value(inputs, "export_path")
            ros_distro = get_selected_item(inputs, "ros_distro")
            generate_launch = get_bool_value(inputs, "generate_launch")
            generate_rviz = get_bool_value(inputs, "generate_rviz")
            generate_gazebo = get_bool_value(inputs, "generate_gazebo")
            generate_control = get_bool_value(inputs, "generate_control")

            export_config = ExportConfig(
                robot_name=robot_name,
                export_directory=export_directory,
                ros_distro=ros_distro or "jazzy",
                generate_urdf=True,
                generate_xacro=True,
                generate_launch=generate_launch,
                generate_rviz=generate_rviz,
                generate_gazebo=generate_gazebo,
                generate_ros2_control=generate_control
            )

            result = Validator(export_config).validate()
            if not result["valid"]:
                ui.messageBox("\n".join(result["errors"]))
                return

            manager = ExportManager(export_config)
            robot = manager.export()
            if robot is None:
                ui.messageBox(
                    "Export failed. No files were generated. Check the FusionToDescription "
                    "Text Commands/log output for the exact error."
                )
                return

            package_dir = export_config.export_directory + "/" + export_config.package_name
            ui.messageBox(
                "Export completed successfully.\n\n"
                f"Package: {export_config.package_name}\n"
                f"Location: {package_dir}"
            )

        except Exception as error:
            if ui is None:
                ui = self.get_ui()
            if ui:
                ui.messageBox(
                    f"Export Error: {str(error)}\n\n{traceback.format_exc()}"
                )
