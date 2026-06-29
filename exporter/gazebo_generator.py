"""
gazebo_generator.py

Generates Gazebo-specific resources (worlds, bridge config, etc).

FIXED:
- Added config parameter
- Harmonic-compatible configuration
- Bridge configuration template
"""

from .file_writer import FileWriter
import os


class GazeboGenerator:

    def __init__(
        self,
        robot,
        package_creator,
        config=None
    ):
        """
        Initialize Gazebo generator.
        
        Args:
            robot: RobotModel instance
            package_creator: PackageCreator instance
            config: ExportConfig instance (for Harmonic-specific config)
        """

        self.robot = robot
        self.package = package_creator
        self.config = config  # ✅ ADDED: Use for Harmonic configuration

        self.writer = FileWriter(
            self.package.package_directory()
        )

    # =====================================================
    # Generate Gazebo Resources
    # =====================================================

    def generate(self):
        """Generate all Gazebo-related resources."""

        # Generate empty world
        self.writer.write_file(
            "worlds/empty.sdf",
            self._build_empty_world()
        )

        # ✅ ADDED: Generate bridge configuration
        self.writer.write_file(
            "config/bridge_config.yaml",
            self._build_bridge_config()
        )

        # ✅ ADDED: Generate Gazebo configuration
        self.writer.write_file(
            "config/gazebo_sim.rviz",
            self._build_gazebo_rviz_config()
        )

    # =====================================================
    # Build Empty World
    # =====================================================

    def _build_empty_world(self):
        """Build Gazebo world SDF file."""

        world = """<?xml version="1.0"?>
<sdf version="1.9">
  <world name="default">

    <!-- Physics -->
    <physics type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>

    <!-- Gravity -->
    <gravity>0 0 -9.81</gravity>

    <!-- Sun -->
    <light name="sun" type="directional">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <!-- Ground Plane -->
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
            <specular>0.8 0.8 0.8 1</specular>
          </material>
        </visual>
      </link>
    </model>

  </world>
</sdf>
"""
        return world

    # =====================================================
    # Build Bridge Configuration
    # =====================================================

    def _build_bridge_config(self):
        """Build ros_gz_bridge configuration YAML."""

        bridge_config = """- ros_topic_name: "clock"
  gz_topic_name: "clock"
  ros_type_name: "rosgraph_msgs/msg/Clock"
  gz_type_name: "gz.msgs.Clock"
  direction: GZ_TO_ROS

- ros_topic_name: "joint_states"
  gz_topic_name: "joint_states"
  ros_type_name: "sensor_msgs/msg/JointState"
  gz_type_name: "gz.msgs.Model"
  direction: GZ_TO_ROS

- ros_topic_name: "odom"
  gz_topic_name: "odom"
  ros_type_name: "nav_msgs/msg/Odometry"
  gz_type_name: "gz.msgs.Odometry"
  direction: GZ_TO_ROS

- ros_topic_name: "cmd_vel"
  gz_topic_name: "cmd_vel"
  ros_type_name: "geometry_msgs/msg/Twist"
  gz_type_name: "gz.msgs.Twist"
  direction: ROS_TO_GZ

- ros_topic_name: "scan"
  gz_topic_name: "scan"
  ros_type_name: "sensor_msgs/msg/LaserScan"
  gz_type_name: "gz.msgs.LaserScan"
  direction: GZ_TO_ROS

- ros_topic_name: "camera/image_raw"
  gz_topic_name: "camera/image_raw"
  ros_type_name: "sensor_msgs/msg/Image"
  gz_type_name: "gz.msgs.Image"
  direction: GZ_TO_ROS

- ros_topic_name: "imu"
  gz_topic_name: "imu"
  ros_type_name: "sensor_msgs/msg/Imu"
  gz_type_name: "gz.msgs.IMU"
  direction: GZ_TO_ROS
"""

        return bridge_config

    # =====================================================
    # Build Gazebo RViz Config
    # =====================================================

    def _build_gazebo_rviz_config(self):
        """Build RViz configuration for Gazebo visualization."""

        config = """# RViz configuration for Gazebo simulation visualization
# Shows both robot model and Gazebo world

Panels:
  - Class: rviz_common/Displays
    Name: Displays

Visualization Manager:
  Class: ""
  Displays:
    - Class: rviz_common/RobotModel
      Description Topic: robot_description
      Enabled: true
      Name: RobotModel
      TF Prefix: ""
      Value: true
      Visual Enabled: true
"""

        return config
