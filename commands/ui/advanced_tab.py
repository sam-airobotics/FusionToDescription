"""
Advanced tab for the export dialog.

Includes mesh format selection and file generation options.
"""

from ..helpers.ui_builder import (
    create_bool_input,
    create_group,
    create_radio_group
)


def build_advanced_tab(inputs):
    """Build the Advanced tab UI.
    
    Args:
        inputs: The command's commandInputs container
        
    Returns:
        The created TabCommandInput
    """
    advanced_tab = inputs.addTabCommandInput(
        "advanced_tab",
        "Advanced"
    )

    advanced_inputs = advanced_tab.children

    # Mesh export settings
    mesh_group = create_group(
        advanced_inputs,
        "mesh_group",
        "Mesh Export"
    )

    mesh_inputs = mesh_group.children

    create_radio_group(
        mesh_inputs,
        "mesh_format",
        "Mesh Format",
        [
            ("STL", True),
            ("OBJ", False),
        ]
    )

    # File generation options
    file_group = create_group(
        advanced_inputs,
        "file_group",
        "Generated Files"
    )

    file_inputs = file_group.children

    create_bool_input(
        file_inputs,
        "gen_package_xml",
        "package.xml",
        True
    )

    create_bool_input(
        file_inputs,
        "gen_cmakelists",
        "CMakeLists.txt",
        True
    )

    create_bool_input(
        file_inputs,
        "gen_launch_files",
        "Launch Files",
        True
    )

    create_bool_input(
        file_inputs,
        "gen_rviz_file",
        "RViz Config",
        True
    )

    create_bool_input(
        file_inputs,
        "gen_gazebo_file",
        "Gazebo Config",
        True
    )

    create_bool_input(
        file_inputs,
        "gen_ros2_control",
        "ros2_control",
        True
    )

    return advanced_tab
