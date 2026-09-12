"""Execute handler for the FusionToDescription export command."""

import traceback

import adsk.core

from .helpers.input_utils import get_bool_value, get_selected_item, get_string_value
from ..exporter.export_config import ExportConfig
from ..exporter.export_manager import ExportManager
from ..utils.validate import Validator


class ExecuteHandler(adsk.core.CommandEventHandler):
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

            inputs = args.firingEvent.sender.commandInputs
            export_config = ExportConfig(
                robot_name=get_string_value(inputs, "robot_name"),
                export_directory=get_string_value(inputs, "export_path"),
                ros_distro=get_selected_item(inputs, "ros_distro") or "jazzy",
                generate_urdf=True,
                generate_xacro=True,
                generate_launch=get_bool_value(inputs, "generate_launch"),
                generate_rviz=get_bool_value(inputs, "generate_rviz"),
                generate_gazebo=get_bool_value(inputs, "generate_gazebo"),
                generate_ros2_control=get_bool_value(inputs, "generate_control"),
            )
            result = Validator(export_config).validate()
            if not result["valid"]:
                ui.messageBox("Export configuration error:\n\n" + "\n".join(result["errors"]))
                return

            robot = ExportManager(export_config).export()
            package_dir = export_config.package_directory() if hasattr(export_config, "package_directory") else (
                export_config.export_directory + "/" + export_config.package_name
            )
            ui.messageBox(
                "Export completed successfully.\n\n"
                f"Package: {export_config.package_name}\n"
                f"Location: {package_dir}\n\n"
                f"Links: {len(robot.links)}\n"
                f"Joints: {len(robot.joints)}"
            )
        except Exception as error:
            if ui is None:
                try:
                    ui = self.get_ui()
                except Exception:
                    ui = None
            if ui:
                ui.messageBox(f"Export Error:\n\n{error}\n\n{traceback.format_exc()}")
