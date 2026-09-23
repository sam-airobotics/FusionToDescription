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

    Layout:
        Robot Name  [____________________________]
        Export Path [____________________________]  [Browse]
    """
    general_tab = inputs.addTabCommandInput(
        "general_tab",
        "General"
    )

    general_inputs = general_tab.children

    # Robot name input.
    create_string_input(
        general_inputs,
        "robot_name",
        "Robot Name",
        ""
    )

    # Export Path row.
    #
    # Fusion's TableCommandInput supports read-only StringValueCommandInput
    # cells for displaying simple text. Use that for the label so it matches
    # the normal command-input label appearance while keeping the editable
    # path field and Browse button on the same row.
    #
    # Layout:
    # Export Path [____________________________]  [Browse]
    export_path_table = general_inputs.addTableCommandInput(
        "export_path_row",
        "",
        4,
        "18:62:5:15"
    )
    export_path_table.hasGrid = False
    export_path_table.columnSpacing = 8
    export_path_table.minimumVisibleRows = 1
    export_path_table.maximumVisibleRows = 1

    # Export Path label.
    export_path_label = general_inputs.addStringValueInput(
        "export_path_label",
        "",
        "Export Path"
    )
    export_path_label.isReadOnly = True
    export_path_table.addCommandInput(export_path_label, 0, 0)

    # Export Path textbox.
    export_path_input = general_inputs.addStringValueInput(
        "export_path",
        "",
        ""
    )
    export_path_table.addCommandInput(export_path_input, 0, 1)

    # Spacer between textbox and Browse button.
    export_path_spacer = general_inputs.addStringValueInput(
        "export_path_spacer",
        "",
        ""
    )
    export_path_spacer.isReadOnly = True
    export_path_table.addCommandInput(export_path_spacer, 0, 2)

    # Browse push button.
    browse_button = general_inputs.addBoolValueInput(
        "browse_export_path",
        "Browse",
        False,
        "",
        False
    )
    browse_button.isFullWidth = True
    export_path_table.addCommandInput(browse_button, 0, 3)

    # ROS Distro selection.
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

    # Generate options.
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
