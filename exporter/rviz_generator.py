"""
rviz_generator.py

Generates a default RViz2 configuration for the
exported robot description package.
"""

from .file_writer import FileWriter


class RVizGenerator:

    def __init__(
        self,
        robot,
        package_creator
    ):

        self.robot = robot
        self.package = package_creator

        self.writer = FileWriter(
            self.package.package_directory()
        )

    # =====================================================
    # Generate RViz Config
    # =====================================================

    def generate(self):

        self.writer.write_file(
            f"rviz/{self.robot.robot_name}.rviz",
            self._build()
        )

    # =====================================================
    # Build RViz Configuration
    # =====================================================

    def _build(self):

        return f"""Panels:
  - Class: rviz_common/Displays
    Name: Displays

  - Class: rviz_common/Views
    Name: Views

Visualization Manager:

  Class: ""

  Displays:

    - Class: rviz_default_plugins/Grid
      Name: Grid
      Enabled: true
      Cell Size: 1
      Plane Cell Count: 20
      Color: 160;160;160

    - Class: rviz_default_plugins/RobotModel
      Name: Robot Model
      Enabled: true
      Description Topic:
        Value: robot_description
      Alpha: 1

    - Class: rviz_default_plugins/TF
      Name: TF
      Enabled: true
      Show Axes: true
      Show Names: true

    - Class: rviz_default_plugins/Axes
      Name: World Axes
      Enabled: true
      Length: 1
      Radius: 0.05

  Global Options:
    Fixed Frame: base_link
    Background Color: 48;48;48
    Frame Rate: 30

  Tools:

    - Class: rviz_default_plugins/Interact

    - Class: rviz_default_plugins/MoveCamera

    - Class: rviz_default_plugins/Select

    - Class: rviz_default_plugins/FocusCamera

  Views:

    Current:

      Class: rviz_default_plugins/Orbit

      Distance: 3

      Focal Point:
        X: 0
        Y: 0
        Z: 0

      Pitch: 0.6
      Yaw: 0.8

Window Geometry:

  Width: 1600
  Height: 900
  X: 50
  Y: 50
"""