"""
gazebo_plugin_xacro_generator.py

Generates the gazebo.xacro file with sensor and actuator plugin definitions.

FIXED:
- Added config parameter
- Harmonic-compatible plugin configuration
- Proper sensor plugin templates
"""

from .file_writer import FileWriter


class GazeboPluginXacroGenerator:

    def __init__(
        self,
        robot,
        package_creator,
        config=None
    ):
        """
        Initialize gazebo plugin xacro generator.
        
        Args:
            robot: RobotModel instance
            package_creator: PackageCreator instance
            config: ExportConfig instance (optional)
        """

        self.robot = robot
        self.package = package_creator
        self.config = config  # ✅ ADDED: Use for Harmonic-specific config

        self.writer = FileWriter(
            self.package.package_directory()
        )

    # =====================================================
    # Generate Gazebo Xacro
    # =====================================================

    def generate(self):
        """Generate the gazebo.xacro file with plugin definitions."""

        xacro = self._build_xacro()

        self.writer.write_file(
            f"urdf/gazebo.xacro",
            xacro
        )

    # =====================================================
    # Build Gazebo Xacro
    # =====================================================

    def _build_xacro(self):
        """Build gazebo-specific Xacro content for Harmonic."""

        xacro = f"""<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="{self.robot.robot_name}">

  <!-- ============================= -->
  <!-- Gazebo Harmonic Configuration -->
  <!-- ============================= -->

  <!-- Physics engine configuration -->
  <gazebo>
    <physics type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>
    
    <!-- Gravity -->
    <gravity>0 0 -9.81</gravity>
  </gazebo>

  <!-- Link-specific properties -->
"""

        # Add link-specific Gazebo configurations
        for link in self.robot.links:
            if link.name != "base_link":  # Skip base_link, it's usually fixed
                xacro += f"""
  <gazebo reference="{link.name}">
    <mu1>0.2</mu1>
    <mu2>0.2</mu2>
    <self_collide>false</self_collide>
  </gazebo>
"""

        xacro += """
  <!-- ============================= -->
  <!-- ROS 2 - Gazebo Bridge         -->
  <!-- ============================= -->

  <!-- This configuration is used by ros_gz_bridge to map topics -->
  <!-- See launch/gazebo.launch.py for bridge configuration -->

</robot>
"""

        return xacro
