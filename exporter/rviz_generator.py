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
        """Build RViz configuration content."""

        config = f"""Panels:
- Class: rviz_common/Displays
  Help Height: 78
  Name: Displays
  Property Tree Widget:
    Expanded:
      - /Global Options1
      - /Status1
    Splitter Ratio: 0.5
  Tree Height: 775
- Class: rviz_common/Selection
  Name: Selection
- Class: rviz_common/Tool Properties
  Collapsed: false
  Name: Tool Properties
  Splitter Ratio: 0.588679
- Class: rviz_common/Views
  Expanded:
    - /Current View1
  Name: Views
  Splitter Ratio: 0.5

Visualization Manager:
  Class: ""
  Displays:
    - Alpha: 0.5
      Cell Size: 1
      Class: rviz_common/Grid
      Color: 160; 160; 164
      Enabled: true
      Line Style:
        Line Width: 0.03
        Value: Line
      Name: Grid
      Normal Cell Count: 0
      Offset:
        X: 0
        Y: 0
      Plane: XY
      Plane Cell Count: 10
      Reference Frame: <Fixed Frame>
      Value: true
    - Alpha: 1
      Class: rviz_common/RobotModel
      Description Topic: robot_description
      Enabled: true
      Links:
        All Links Enabled: true
      Name: RobotModel
      TF Prefix: ""
      Update Interval: 0
      Value: true
      Visual Enabled: true
  Enabled: true
  Global Options:
    Background Color: 48; 48; 48
    Fixed Frame: world
    Frame Rate: 30
  Name: root
  Tools:
    - Class: rviz_common/Interact
      Hide Inactive Objects: true
    - Class: rviz_common/MoveCamera
    - Class: rviz_common/Select
    - Class: rviz_common/FocusCamera
    - Class: rviz_common/Measure
    - Class: rviz_common/SetInitialPose
      Theta std deviation: 0.26179938779914946
      Topic:
        Depth: 5
        Durability Policy: Volatile
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /initialpose
      X std deviation: 0.5
      Y std deviation: 0.5
    - Class: rviz_common/SetGoal
      Topic:
        Depth: 5
        Durability Policy: Volatile
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /goal_pose
  Value: true
  Views:
    Current:
      Angle: 0
      Class: rviz_common/Orbit
      Distance: 3
      Enable Stereo Rendering:
        Stereo Eye Separation: 0.06
        Stereo Focal Distance: 1
        Swap Stereo Eyes: false
        Value: false
      Focal Point:
        X: 0
        Y: 0
        Z: 0
      Focal Shape Fixed Size: true
      Focal Shape Size: 0.05
      Invert Z Axis: false
      Name: Current View
      Near Clip Distance: 0.01
      Pitch: 0.5
      Target Frame: <Fixed Frame>
      Value: Orbit (rviz)
      Yaw: 0.5
    Saved Views: {{}}
Window Geometry:
  Displays:
    collapsed: false
  Height: 876
  Hide Left Dock: false
  Hide Right Dock: true
  QMainWindow State: 000000ff00000000fd00000004000000000000015600000300fc0200000005fb0000001200530065006c0065006300740069006f006e00000000000000015600000000000000000fb000000120056006900650077007300200054006f006f006b00690074010000015600000226000001e000fffb0000001e0054006f006f006c002000500072006f0070006500720074006900650073010000038c0000015f0000000000000000fb0000001200440069007300700006c0061007900730000000000000003000000000000000000000004fc0000030000000004000000040000000800000008fc0000000100000002000000010000000a0054006f006f006c00420061007200000000000000ffffffff0000000000000000
  Selection:
    collapsed: false
  Tool Properties:
    collapsed: false
  Views:
    collapsed: true
  Width: 1280
"""

        return config
