# 🚀 FusionToDescription v0.1.1

## Material Pipeline Update

Version **0.1.1** builds upon the initial public release by introducing a redesigned material pipeline, improved export architecture, and numerous internal improvements to the ROS 2 package generation workflow.

This release focuses on making exported robot descriptions more modular, maintainable, and ready for future rendering enhancements while continuing work on improving joint generation.

---

# ✨ What's New

## 🎨 Material Pipeline Overhaul

FusionToDescription now features a completely redesigned material pipeline.

### ✅ Fusion Material Preservation

The exporter now preserves the original Autodesk Fusion 360 material (appearance) assigned to every component.

Instead of replacing materials with predefined colors, Fusion material names are now stored throughout the export process.

### 🌈 Independent Visualization Colors

Visualization colors are now separated from Fusion materials.

This enables:

- Preserve original Fusion material names
- Assign visualization colors independently
- Better compatibility with RViz
- Better compatibility with Gazebo
- Cleaner material management throughout the package

---

## ⚙️ Improved Robot Model

The internal RobotModel has been redesigned to support richer material information.

Instead of storing materials as plain strings:

```python
material = "Steel"
```

FusionToDescription now stores:

```python
Material
├── name
└── Color
      ├── r
      ├── g
      ├── b
      └── a
```

This architecture prepares the exporter for future features including:

- Material libraries
- Custom shaders
- PBR materials
- Texture support
- Advanced Gazebo rendering

---

## 📦 Improved Material Generation

The generated `materials.xacro` file has been completely redesigned.

### Improvements

- Automatic material generation
- Duplicate material removal
- RGBA color generation
- Material definitions shared between links
- Cleaner Xacro output
- Better compatibility with ROS 2

---

## 🖥️ Updated Properties Tab

The **Properties** tab has been extended to include material visualization settings.

Users can now:

- View the original Fusion material
- Choose visualization colors independently
- Keep CAD materials unchanged while customizing simulation appearance

<p align="center">
<img src="https://github.com/user-attachments/assets/20838993-53f1-423e-8d91-57416fa8c59b" width="95%"><br>
<img width="95%" src="https://github.com/user-attachments/assets/0c63a336-9e4d-494e-ad95-ef5198d9e5c3">
</p>

---

# ⚡ Export Pipeline Improvements

Several internal components have been redesigned to improve maintainability and future development.

### Updated Components

- Material Parser
- RobotModel
- Export Manager
- Materials Xacro Generator
- Link Generation Pipeline
- URDF Generation Pipeline

### Improvements

- Better separation of responsibilities
- Cleaner data flow
- Improved code organization
- Simplified material handling
- Easier future feature integration

---

# 📦 Export Result

FusionToDescription continues to automatically generate a complete ROS 2 description package containing:

- URDF / Xacro
- Meshes
- Material definitions
- Gazebo configuration
- RViz configuration
- Launch files
- ROS 2 Control configuration (optional)

<p align="center">
<img src="https://github.com/user-attachments/assets/71ecfa46-278c-4e3f-9ab4-1984b865d32c" width="95%">
</p>

---

# 📁 Export Location

Generated packages are exported directly to the selected destination.

<p align="center">
<img src="https://github.com/user-attachments/assets/a2719525-de13-4f5d-835d-5cd502457a16" width="95%">
</p>

---

# 🚀 Release Highlights

- ✅ Redesigned Material Pipeline
- ✅ Fusion Material Preservation
- ✅ Independent Visualization Colors
- ✅ Improved RobotModel Architecture
- ✅ Automatic Material Generation
- ✅ Cleaner `materials.xacro`
- ✅ Improved Export Pipeline
- ✅ Updated URDF/Xacro Generation
- ✅ Better Package Structure
- ✅ Improved Code Maintainability

---

# 🚧 Known Issues

FusionToDescription is still under active development.

The following areas are currently being improved:

- Joint origin extraction
- Joint orientation generation
- Joint axis calculation
- Exported package syntax validation

Some complex robot assemblies may still require minor manual adjustments before simulation.

---

# 🔜 Coming in the Next Release

Development is now focused on improving the robot kinematic pipeline and export reliability.

Planned improvements include:

- 🔗 Complete joint generation pipeline
- 📐 Accurate joint origin extraction
- 🧭 Improved joint orientation handling
- ⚙️ Better URDF/Xacro validation
- 🤖 More reliable ROS 2 description packages
- 🎨 Additional UI improvements
- ⚡ Faster export performance
- 🛠️ General bug fixes and stability improvements

Stay tuned for the next release!
