"""
rviz_generator.py

Generates RViz configuration file for robot visualization.

FIXED: Added config parameter for consistency
"""

from .file_writer import FileWriter

class RVizGenerator:

    def __init__(
        self,
        robot,
        package_creator,
        config=None
    ):
        """
        Initialize RViz generator.
        
        Args:
            robot: RobotModel instance
            package_creator: PackageCreator instance
            config: ExportConfig instance (optional)
        """

        self.robot = robot
        self.package = package_creator
        self.config = config  # ✅ ADDED

        self.writer = FileWriter(
            self.package.package_directory()
        )

    # =====================================================
    # Generate RViz Config
    # =====================================================

    def generate(self):
        """Generate the RViz configuration file."""

        config = self._build_rviz_config()

        self.writer.write_file(
            f"rviz/{self.robot.robot_name}.rviz",
            config
        )

    # =====================================================
    # Build RViz Config
    # =====================================================

    def _build_rviz_config(self):
        """Build RViz configuration content compatible with ROS 2 Humble/Jazzy."""

        fixed_frame = (
            "base_footprint"
            if any(link.name == "base_footprint" for link in self.robot.links)
            else "base_link"
        )

        config = f"""Panels:
- Class: rviz_common/Displays
  Name: Displays
- Class: rviz_common/Selection
  Name: Selection
- Class: rviz_common/Tool Properties
  Name: Tool Properties
- Class: rviz_common/Views
  Name: Views

Visualization Manager:
  Class: ""
  Displays:

    - Name: Grid
      Class: rviz_default_plugins/Grid
      Enabled: true
      Cell Size: 1
      Plane: XY
      Plane Cell Count: 20
      Color: 160;160;164
      Alpha: 0.5
      Line Style:
        Value: Lines
        Line Width: 0.03
      Offset:
        X: 0
        Y: 0
        Z: 0

    - Name: RobotModel
      Class: rviz_default_plugins/RobotModel
      Enabled: true
      Description Source: Topic
      Description Topic:
        Value: /robot_description
      Alpha: 1
      Visual Enabled: true
      Collision Enabled: false
      Update Interval: 0

    - Name: TF
      Class: rviz_default_plugins/TF
      Enabled: true
      Frame Timeout: 15
      Marker Scale: 0.3
      Show Axes: true
      Show Arrows: true
      Show Names: true

    - Name: Axes
      Class: rviz_default_plugins/Axes
      Enabled: true
      Length: 0.3
      Radius: 0.03

  Enabled: true

  Global Options:
    Fixed Frame: {fixed_frame}
    Background Color: 48;48;48
    Frame Rate: 30

  Name: root

  Tools:
    - Class: rviz_default_plugins/Interact
    - Class: rviz_default_plugins/MoveCamera
    - Class: rviz_default_plugins/Select
    - Class: rviz_default_plugins/FocusCamera
    - Class: rviz_default_plugins/Measure

    - Class: rviz_default_plugins/SetInitialPose
      Topic:
        Value: /initialpose

    - Class: rviz_default_plugins/SetGoal
      Topic:
        Value: /goal_pose

  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 3
      Focal Point:
        X: 0
        Y: 0
        Z: 0
      Pitch: 0.5
      Yaw: 0.5
      Near Clip Distance: 0.01
      Target Frame: {fixed_frame}
      Value: Orbit

Window Geometry:
  Height: 900
  Width: 1400
"""

        return config