"""
gazebo_generator.py

Generates Gazebo Harmonic resources for the exported robot.
"""

from .file_writer import FileWriter


class GazeboGenerator:

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
    # Generate Gazebo Resources
    # =====================================================

    def generate(self):

        self.writer.write_file(
            "urdf/gazebo_plugins.xacro",
            self._generate_gazebo_plugins()
        )

        self.writer.write_file(
            "worlds/empty.world",
            self._generate_world()
        )

    # =====================================================
    # Gazebo Plugins
    # =====================================================

    def _generate_gazebo_plugins(self):

        xml = f"""<?xml version="1.0"?>

<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Gazebo Harmonic Configuration -->

  <gazebo>

    <plugin
      filename="gz-sim-joint-state-publisher-system"
      name="gz::sim::systems::JointStatePublisher"/>

    <plugin
      filename="gz-sim-pose-publisher-system"
      name="gz::sim::systems::PosePublisher"/>

  </gazebo>

</robot>
"""

        return xml

    # =====================================================
    # Empty World
    # =====================================================

    def _generate_world(self):

        world = """<?xml version="1.0" ?>

<sdf version="1.9">

  <world name="default">

    <plugin
      filename="gz-sim-physics-system"
      name="gz::sim::systems::Physics"/>

    <plugin
      filename="gz-sim-user-commands-system"
      name="gz::sim::systems::UserCommands"/>

    <plugin
      filename="gz-sim-scene-broadcaster-system"
      name="gz::sim::systems::SceneBroadcaster"/>

    <gravity>0 0 -9.81</gravity>

    <scene>

      <ambient>0.4 0.4 0.4 1</ambient>

      <background>0.7 0.7 0.7 1</background>

    </scene>

    <light name="sun" type="directional">

      <cast_shadows>true</cast_shadows>

      <pose>0 0 10 0 0 0</pose>

      <diffuse>0.8 0.8 0.8 1</diffuse>

      <specular>0.2 0.2 0.2 1</specular>

      <direction>-0.5 0.1 -0.9</direction>

    </light>

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

        </visual>

      </link>

    </model>

  </world>

</sdf>
"""

        return world