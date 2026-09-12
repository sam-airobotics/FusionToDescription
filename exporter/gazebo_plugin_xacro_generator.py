"""Generate Gazebo Harmonic-specific URDF/Xacro extensions."""

from .file_writer import FileWriter
from xml.sax.saxutils import escape, quoteattr


class GazeboPluginXacroGenerator:
    def __init__(self, robot, package_creator, config=None):
        self.robot = robot
        self.package = package_creator
        self.config = config
        self.writer = FileWriter(self.package.package_directory())

    def generate(self):
        return self.writer.write_file("urdf/gazebo.xacro", self._build_xacro())

    def _build_xacro(self):
        xacro = f'<?xml version="1.0"?>\n<robot name={quoteattr(self.robot.robot_name)} xmlns:xacro="http://www.ros.org/wiki/xacro">\n'
        material_map = {
            "Black": "Gazebo/Black", "Blue": "Gazebo/Blue", "Green": "Gazebo/Green",
            "Red": "Gazebo/Red", "Silver": "Gazebo/Grey", "Yellow": "Gazebo/Yellow",
            "White": "Gazebo/White", "Gray": "Gazebo/Grey",
        }
        for link in self.robot.links:
            material_name = getattr(link.material, "name", None)
            gazebo_material = material_map.get(material_name, "Gazebo/Grey")
            xacro += f'''  <gazebo reference={quoteattr(link.name)}>
    <material>{gazebo_material}</material>
    <mu1>0.2</mu1>
    <mu2>0.2</mu2>
    <self_collide>false</self_collide>
    <gravity>true</gravity>
  </gazebo>
'''

        moving_joints = [j for j in self.robot.joints if j.joint_type != "fixed"]
        if moving_joints:
            xacro += '''  <gazebo>
    <plugin filename="gz-sim-joint-state-publisher-system" name="gz::sim::systems::JointStatePublisher">
      <topic>joint_states</topic>
'''
            for joint in moving_joints:
                xacro += f'      <joint_name>{escape(joint.name)}</joint_name>\n'
            xacro += '    </plugin>\n  </gazebo>\n'

        return xacro + '</robot>\n'
