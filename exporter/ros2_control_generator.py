"""
ros2_control_generator.py

Generates ROS 2 Control configuration and launch files.

FIXED:
- Added config parameter
- Complete implementation (was stubbed out)
- Hardware interface configuration
- Controller configuration
"""

from .file_writer import FileWriter


class ROS2ControlGenerator:

    def __init__(
        self,
        robot,
        package_creator,
        config=None
    ):
        """
        Initialize ROS 2 Control generator.
        
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
    # Generate ROS 2 Control Files
    # =====================================================

    def generate(self):
        """Generate ROS 2 Control configuration files."""

        # Generate hardware interface configuration
        self.writer.write_file(
            "config/ros2_control.yaml",
            self._build_control_config()
        )

        # Generate controllers configuration
        self.writer.write_file(
            "config/controllers.yaml",
            self._build_controllers_config()
        )

        # Generate control launch file
        self.writer.write_file(
            "launch/controllers.launch.py",
            self._build_controllers_launch()
        )

    # =====================================================
    # Build Control Configuration
    # =====================================================

    def _build_control_config(self):
        """Build ros2_control configuration."""

        config = f"""# ROS 2 Control Configuration for {self.robot.robot_name}

controller_manager:
  ros__parameters:
    update_rate: 100  # Hz

    # Load these controllers
    joint_trajectory_controller:
      type: joint_trajectory_controller/JointTrajectoryController
    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

# Hardware interface (Gazebo plugin)
{self.robot.robot_name}_hardware:
  ros__parameters:
    use_sim_time: true
    hardware:
      type: gazebo_ros2_control/GazeboSystem
    joints:
"""

        # Add joints
        for joint in self.robot.joints:
            if joint.joint_type != "fixed":
                config += f"""      - name: {joint.name}
        state:
          interface_names:
            - position
            - velocity
        command:
          interface_names:
            - position
            - velocity
"""

        return config

    # =====================================================
    # Build Controllers Configuration
    # =====================================================

    def _build_controllers_config(self):
        """Build controllers configuration."""

        config = f"""# ROS 2 Controllers Configuration

controller_manager:
  ros__parameters:
    update_rate: 100

    # Controller names
    joint_trajectory_controller:
      type: joint_trajectory_controller/JointTrajectoryController
    
    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

# Joint Trajectory Controller
joint_trajectory_controller:
  ros__parameters:
    joints:
"""

        # Add controllable joints
        for joint in self.robot.joints:
            if joint.joint_type != "fixed":
                config += f"""      - {joint.name}
"""

        config += """
    command_interfaces:
      - position
      - velocity
    
    state_interfaces:
      - position
      - velocity
    
    state_publish_rate: 50.0
    action_monitor_rate: 20.0
    allow_partial_joints_goal: true
    
    constraints:
      stopped_velocity_tolerance: 0.01
      goal_time: 0.0
      {joint_name}: 
        trajectory: 0.0
        goal: 0.0

# Joint State Broadcaster
joint_state_broadcaster:
  ros__parameters:
    use_sim_time: true
"""

        return config

    # =====================================================
    # Build Controllers Launch File
    # =====================================================

    def _build_controllers_launch(self):
        """Build controllers launch file."""

        package = self.robot.package_name

        launch = f'''"""
ROS 2 Control launch file for {self.robot.robot_name}.
Loads and starts controllers.
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessStart
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    package_name = "{package}"

    config_dir = os.path.join(
        get_package_share_directory(package_name),
        "config"
    )

    # Controller Manager Node
    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[os.path.join(config_dir, "ros2_control.yaml")]
    )

    # Joint State Broadcaster spawner
    joint_state_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
        output="screen"
    )

    # Joint Trajectory Controller spawner
    joint_trajectory_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_trajectory_controller"],
        output="screen"
    )

    return LaunchDescription([
        controller_manager,
        joint_state_spawner,
        joint_trajectory_spawner
    ])
'''

        return launch
