# 🚀 FusionToDescription v0.1.3

## Export Path & Browse Feature

Version **0.1.3** introduces an improved **Export Path workflow** with an integrated **Browse** option in the FusionToDescription export dialog.

Users can now select the destination folder through the Fusion 360 folder picker instead of entering the complete export path manually.

The selected folder is displayed directly in the **Export Path** field and is then used as the destination for the generated ROS 2 description package.

---

# ✨ What's New

## 📁 Export Path Browse

The General tab now provides a dedicated Browse control next to the Export Path field.

The interface follows this layout:

```text
Robot Name  [____________________________]

Export Path [____________________________]   [Browse]
```

The Browse control is integrated into the same row as the Export Path field, keeping the export configuration compact and easy to use.

### Browse Workflow

1. Open **FusionToDescription**.
2. Go to the **General** tab.
3. Locate **Export Path**.
4. Click **Browse**.
5. Select the destination folder from the Fusion 360 folder dialog.
6. The selected folder path is automatically inserted into the Export Path field.
7. Continue with the export.

This eliminates the need to manually type or paste long filesystem paths.

---

## 🧭 Fusion 360 Folder Selection

The Browse feature uses Fusion 360's native folder-selection dialog.

The exporter:

- Opens a native Fusion 360 folder picker
- Allows the user to select an existing destination folder
- Retrieves the selected filesystem path
- Updates the Export Path field automatically
- Keeps the selected path available for the export operation
- Safely handles dialog cancellation

The Browse button behaves as a momentary action and does not remain selected after the folder-selection operation.

---

## 🧩 Table-Based Export Path Layout

The Export Path controls are arranged using Fusion 360's `TableCommandInput` API.

The row contains:

- Export Path label
- Editable Export Path textbox
- Spacing between the textbox and button
- Browse button

The Export Path textbox is retrieved from its table cell when the Browse operation completes, ensuring that the selected folder is written to the correct UI input.

This keeps the Browse functionality compatible with the compact single-row layout of the export dialog.

---

# 🔗 Joint Pipeline

FusionToDescription continues to include the redesigned **joint and kinematic frame pipeline** introduced in **v0.1.2**.

The pipeline converts Fusion 360 assembly joints into ROS 2 / URDF joints while preserving the intended assembly structure.

---

## 📐 Accurate Joint Origins

Joint origins are calculated from the relationship between the **parent occurrence frame** and the **Fusion joint frame**.

Conceptually:

```text
URDF joint origin = parent_frame⁻¹ × joint_frame
```

This means the generated URDF joint origin represents the transform:

```text
parent link → joint frame
```

rather than an assembly/world-space pose.

This is important for robots containing nested components, rotated assemblies, or joints whose geometry does not coincide with a component origin.

---

## 🧭 Improved Joint Axis Generation

Movable-joint axes are expressed in the generated **joint frame**.

The pipeline uses Fusion joint motion information where available and transforms the motion axis into the correct joint coordinate system.

Supported motion types include:

- Revolute joints
- Prismatic joints
- Fixed joints

This improves compatibility with ROS 2 controllers, Gazebo, RViz, and downstream kinematic processing.

---

## 🔄 Correct Parent / Child Orientation

Joint orientation is resolved from the complete joint graph instead of assuming that Fusion's endpoint ordering is already suitable for URDF.

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

---

## 🧩 Correct Link-Local Geometry Frames

The exporter separates the **joint transform** from the **child link geometry transform**.

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

The child link's visual/collision origin is calculated relative to the joint frame:

```text
child_origin = joint_frame⁻¹ × child_component_frame
```

This prevents the common **double-transform** problem where an assembly/world transform is applied both to the joint and to the link geometry.

---

## 🧱 Assembly-Context Transform Handling

The joint pipeline uses Fusion occurrence assembly-context transforms where appropriate.

This supports components that are positioned or rotated through an assembly occurrence rather than being located at their component-local origin.

---

## ⚙️ Improved Joint Data Model

Joint records retain the internal frame information required to complete the kinematic conversion.

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

---

# 🧪 Validation & Regression Tests

Version **0.1.2** introduced regression coverage for the joint-frame pipeline.

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

These tests target transform errors that can cause exported robots to appear displaced, duplicated, or incorrectly oriented in simulation.

---

# ✅ Improved Export Validation

The package validation layer checks additional joint and link data.

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

- Preservation of original Fusion material names
- Independent visualization colors
- Better RViz compatibility
- Better Gazebo compatibility
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

The package is exported to the destination selected through the **Export Path** field.

---

# ⚠️ Important Simulation Note

The joint-frame pipeline is validated through Python syntax checks and mathematical regression tests.

The Browse workflow and complete export process require the Autodesk Fusion 360 runtime for full validation.

Generated packages should still be tested in the target ROS 2 / Gazebo environment after export.

---

# 📁 Export Location

The export destination can now be selected directly from the FusionToDescription interface.

Use:

```text
General
  └── Export Path
        ├── Path textbox
        └── Browse
```

Click **Browse**, select the desired destination folder, and the selected path will be populated automatically.

<p align="center">
<img src="https://github.com/user-attachments/assets/a2719525-de13-4f5d-835d-5cd502457a16" width="95%">
</p>

---

# 🚀 Release Highlights — v0.1.3

- ✅ Added Export Path Browse button
- ✅ Added native Fusion 360 folder selection
- ✅ Automatically populate Export Path after folder selection
- ✅ Kept Browse and Export Path controls on the same row
- ✅ Improved Export Path UI layout
- ✅ Added safe Browse dialog cancellation handling
- ✅ Preserved the v0.1.2 joint-frame pipeline
- ✅ Preserved joint-frame validation and regression coverage
- ✅ Preserved v0.1.1 material pipeline

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

