"""
General tab for the export dialog.

Includes robot name, export path, ROS distro selection, and output options.
"""

from ..helpers.ui_builder import (
    create_radio_group,
    create_bool_input,
    create_string_input,
    create_group,
)


def build_general_tab(inputs):
    """Build the General tab UI.

    Args:
        inputs: The command's commandInputs container

    Returns:
        The created TabCommandInput
    """
    general_tab = inputs.addTabCommandInput(
        "general_tab",
        "General"
    )

    general_inputs = general_tab.children

    # Robot name input
    create_string_input(
        general_inputs,
        "robot_name",
        "Robot Name",
        ""
    )

    # Export Path + Browse button on the same row.
    # Use a 3-column table so the Export Path label remains visible:
    # [Export Path] [____________________] [Browse]
    export_path_table = general_inputs.addTableCommandInput(
        "export_path_row",
        "",
        3,
        "20:70:10"
    )
    export_path_table.hasGrid = False
    export_path_table.minimumVisibleRows = 1
    export_path_table.maximumVisibleRows = 1

    export_path_label = general_inputs.addTextBoxCommandInput(
        "export_path_label",
        "",
        "Export Path",
        1,
        True
    )
    export_path_table.addCommandInput(export_path_label, 0, 0)

    export_path_input = general_inputs.addStringValueInput(
        "export_path",
        "",
        ""
    )
    export_path_table.addCommandInput(export_path_input, 0, 1)

    browse_button = general_inputs.addBoolValueInput(
        "browse_export_path",
        "Browse",
        False,
        "",
        False
    )
    export_path_table.addCommandInput(browse_button, 0, 2)

    # ROS Distro selection
    distro_group = create_group(
        general_inputs,
        "distro_group",
        "ROS Distro"
    )

    distro_inputs = distro_group.children

    create_radio_group(
        distro_inputs,
        "ros_distro",
        "ROS Distro",
        [
            ("Humble", False),
            ("Jazzy", True),
        ]
    )

    # Generate options
    generate_group = create_group(
        general_inputs,
        "generate_group",
        "Generate"
    )

    generate_inputs = generate_group.children

    create_bool_input(
        generate_inputs,
        "generate_launch",
        "Launch Files",
        True
    )

    create_bool_input(
        generate_inputs,
        "generate_rviz",
        "RViz Config",
        True
    )

    create_bool_input(
        generate_inputs,
        "generate_gazebo",
        "Gazebo Config",
        True
    )

    create_bool_input(
        generate_inputs,
        "generate_control",
        "ros2_control",
        True
    )

    return general_tab
