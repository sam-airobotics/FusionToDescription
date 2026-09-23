# 🚀 FusionToDescription v0.1.2

## Joint Pipeline Update

Version **0.1.2** introduces the redesigned **joint and kinematic frame pipeline**, replacing the earlier joint-generation approach with a frame-aware Fusion 360 → URDF workflow.

This release focuses on accurate joint origins, joint axes, parent/child orientation, and link-local geometry transforms so exported robot descriptions preserve the intended Fusion 360 assembly structure.

---

# ✨ What's New

## 🔗 Joint Pipeline Overhaul

FusionToDescription now uses a dedicated joint-frame pipeline for converting Fusion 360 assembly joints into ROS 2 / URDF joints.

The pipeline distinguishes between:

- Fusion occurrence / component frames
- Fusion joint geometry frames
- URDF parent frames
- URDF joint frames
- URDF child-link frames

This prevents assembly/world transforms from being incorrectly reused as link-local transforms.

---

## 📐 Accurate Joint Origins

Joint origins are now calculated from the relationship between the **parent occurrence frame** and the **Fusion joint frame**.

Conceptually:

```text
URDF joint origin = parent_frame⁻¹ × joint_frame
```

This means the generated URDF joint origin represents the transform:

```text
parent link → joint frame
```

rather than an assembly/world-space pose.

This is especially important for robots containing nested components, rotated assemblies, or joints whose geometry does not coincide with a component origin.

---

## 🧭 Improved Joint Axis Generation

Movable-joint axes are now expressed in the generated **joint frame**.

The pipeline uses Fusion joint motion information where available and transforms the motion axis into the correct joint coordinate system.

Supported motion types include:

- Revolute joints
- Prismatic joints
- Fixed joints

This improves compatibility with ROS 2 controllers, Gazebo, RViz, and downstream kinematic processing.

---

## 🔄 Correct Parent / Child Orientation

Joint orientation is now resolved from the complete joint graph instead of assuming that Fusion's endpoint ordering is already suitable for URDF.

The pipeline:

1. Builds an undirected joint graph
2. Selects the robot root
3. Traverses the connected components
4. Orients each joint from parent → child
5. Corrects the motion direction when a joint is reversed

For reversed revolute or prismatic joints:

```text
axis_new = -axis_old
```

Joint limits are also transformed consistently:

```text
lower_new = -upper_old
upper_new = -lower_old
```

This keeps the generated kinematics physically consistent after parent/child reversal.

---

## 🧩 Correct Link-Local Geometry Frames

The exporter now separates the **joint transform** from the **child link geometry transform**.

The generated relationship is:

```text
parent link
     ↓
joint origin
     ↓
joint frame
     ↓
child link / CAD component frame
     ↓
visual / collision geometry
```

The child link's visual/collision origin is therefore calculated relative to the joint frame:

```text
child_origin = joint_frame⁻¹ × child_component_frame
```

This prevents the common **double-transform** problem where an assembly/world transform is applied both to the joint and to the link geometry.

It also supports CAD designs where the component origin is not coincident with the joint origin.

---

## 🧱 Assembly-Context Transform Handling

The joint pipeline now uses Fusion occurrence assembly-context transforms where appropriate.

This is important for components that are positioned or rotated through an assembly occurrence rather than being located at their component-local origin.

The exporter no longer treats a component's world/assembly transform as if it were automatically a URDF link-local visual transform.

---

## ⚙️ Improved Joint Data Model

Joint records now retain the internal frame information required to complete the kinematic conversion.

The pipeline tracks:

- Parent frame
- Child frame
- Joint frame
- World motion axis
- Joint-local axis
- Joint origin
- Child-link local origin
- Joint limits

Frame-dependent values are finalized after parent/child orientation has been resolved.

This keeps graph traversal and coordinate-frame calculations separate and makes the export pipeline easier to validate.

---

# 🧪 Validation & Regression Tests

Version **0.1.2** adds regression coverage for the new joint-frame pipeline.

Tests cover:

### Joint frame transforms

- Parent → joint transform
- Joint → child-component transform
- Link-local geometry offsets
- Vector transformation into joint coordinates

### Reversed joints

- Parent/child reversal
- Motion-axis inversion
- Revolute limit inversion
- Prismatic limit inversion

These tests specifically target the transform errors that can cause exported robots to appear displaced, duplicated, or incorrectly oriented in simulation.

---

# ✅ Improved Export Validation

The package validation layer now checks additional joint and link data.

Validation includes:

- Valid package configuration
- Mesh format
- Finite link origins
- Finite collision origins
- Non-zero movable-joint axes
- Finite joint limits
- Ordered joint limits
- Duplicate parent detection
- Self-joint detection
- Root-link detection
- Link reachability
- Disconnected joint-tree detection

Unbounded revolute joints are also reported as warnings where applicable.

---

# 🎨 Material Pipeline

FusionToDescription continues to preserve the material-pipeline improvements introduced in **v0.1.1**.

### Fusion Material Preservation

The exporter preserves the original Autodesk Fusion 360 material (appearance) assigned to every component.

### Independent Visualization Colors

Visualization colors remain independent from Fusion materials.

This enables:

- Preserve original Fusion material names
- Assign visualization colors independently
- Better compatibility with RViz
- Better compatibility with Gazebo
- Cleaner material management

---

# 📦 Export Result

FusionToDescription generates a ROS 2 description package containing:

- URDF / Xacro
- Meshes
- Material definitions
- Gazebo configuration
- RViz configuration
- Launch files
- ROS 2 Control configuration (optional)

---

# ⚠️ Important Simulation Note

The joint-frame pipeline is validated through Python syntax checks and mathematical regression tests.

Full Fusion 360 API execution and Gazebo/RViz simulation remain runtime validation steps because the Autodesk Fusion environment is required to exercise the complete export process.

Generated packages should therefore still be tested in the target ROS 2 / Gazebo environment after export.

---

# 📁 Export Location

Generated packages are exported directly to the selected destination.

<p align="center">
<img src="https://github.com/user-attachments/assets/a2719525-de13-4f5d-835d-5cd502457a16" width="95%">
</p>

---

# 🚀 Release Highlights — v0.1.2

- ✅ Redesigned Joint Pipeline
- ✅ Accurate Joint Frame Extraction
- ✅ Assembly-Context Transform Handling
- ✅ Improved Joint Origin Generation
- ✅ Joint-Local Axis Calculation
- ✅ Automatic Parent/Child Joint Orientation
- ✅ Correct Reversed-Joint Motion Semantics
- ✅ Link-Local Visual/Collision Transforms
- ✅ Improved Joint Limit Handling
- ✅ Stronger URDF Validation
- ✅ Added Joint-Frame Regression Tests
- ✅ Preserved v0.1.1 Material Pipeline
- ✅ Improved Export Architecture

---

# 🔜 Next Development Focus

Future development will continue improving export reliability and simulation compatibility, including:

- 🧩 More complete Fusion joint-type coverage
- 📦 Robust mesh/resource URI handling
- ⚙️ Improved inertial and center-of-mass frame handling
- 🤖 More extensive Gazebo validation
- 🧪 Expanded end-to-end export tests
- 🎨 Additional material and rendering improvements
- ⚡ Export performance and stability improvements

