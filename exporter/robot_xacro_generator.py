"""
robot_xacro_generator.py

Generates the main robot Xacro file.
"""

from xml.sax.saxutils import quoteattr

from .file_writer import FileWriter
from .urdf_generator import URDFGenerator


class RobotXacroGenerator:

    def __init__(
        self,
        robot,
        package_creator,
        config=None
    ):

        self.robot = robot
        self.package = package_creator
        self.config = config

        self.writer = FileWriter(
            self.package.package_directory()
        )

    # =====================================================
    # Generate
    # =====================================================

    def generate(self):

        self.writer.write_file(
            f"urdf/{self.robot.robot_name}.xacro",
            self._build_xacro()
        )

    # =====================================================
    # Build
    # =====================================================

    def _build_xacro(self):

        package = self.robot.package_name

        renderer = URDFGenerator(
            self.robot,
            self.package,
            self.config
        )

        xacro = f"""<?xml version="1.0"?>
<robot
    xmlns:xacro="http://www.ros.org/wiki/xacro"
    name={quoteattr(self.robot.robot_name)}>

    <!-- ============================================== -->
    <!-- Material Definitions                           -->
    <!-- ============================================== -->

    <xacro:include
        filename="$(find {package})/urdf/materials.xacro"/>

"""

        # -------------------------------------------------
        # Gazebo
        # -------------------------------------------------

        if self.config and self.config.generate_gazebo:

            xacro += f"""
    <xacro:include
        filename="$(find {package})/urdf/gazebo.xacro"/>

"""

        # -------------------------------------------------
        # ros2_control
        # -------------------------------------------------

        if self.config and self.config.generate_ros2_control:

            xacro += f"""
    <!--
    <xacro:include
        filename="$(find {package})/urdf/ros2_control.xacro"/>
    -->

"""

        # -------------------------------------------------
        # Base Footprint
        # -------------------------------------------------

        if self._needs_base_footprint():

            xacro += """
    <link name="base_footprint"/>

    <joint
        name="base_joint"
        type="fixed">

        <origin
            xyz="0 0 0"
            rpy="0 0 0"/>

        <parent link="base_footprint"/>

        <child link="base_link"/>

    </joint>

"""

        # -------------------------------------------------
        # Links
        # -------------------------------------------------

        xacro += """
    <!-- ============================================== -->
    <!-- Links                                           -->
    <!-- ============================================== -->
"""

        for link in self.robot.links:

            xacro += renderer._generate_link(
                link,
                xacro=True
            )

        # -------------------------------------------------
        # Joints
        # -------------------------------------------------

        xacro += """
    <!-- ============================================== -->
    <!-- Joints                                          -->
    <!-- ============================================== -->
"""

        for joint in self.robot.joints:

            xacro += renderer._generate_joint(
                joint
            )

        xacro += """

</robot>
"""

        return xacro

    # =====================================================
    # Base Footprint
    # =====================================================

    def _needs_base_footprint(self):

        if self.robot.get_link("base_link") is None:
            return False

        if self.robot.get_link("base_footprint") is not None:
            return False

        return not any(
            joint.child == "base_link"
            for joint in self.robot.joints
        )
