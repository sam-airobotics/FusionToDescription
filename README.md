# 🚀 FusionToDescription v0.1.0

## Initial Public Release

This version introduces a complete end-to-end workflow for exporting Autodesk Fusion 360 robot assemblies into ROS 2 description packages, with an intuitive user interface and automatic package generation.

---

## ✨ What's New

### ✅ Complete Export Workflow

FusionToDescription now provides a complete export pipeline from Fusion 360 to ROS 2.

* Robot package generation
* Automatic URDF/Xacro creation
* Mesh export
* Launch file generation
* RViz configuration
* Gazebo integration

---

## 🖥️ Redesigned User Interface

The exporter now features a four-tab workflow for configuring every aspect of the robot before export.

### 📁 General

Configure the robot name and package export location.

<p align="center">
<img src="https://github.com/user-attachments/assets/64d7088a-0df4-4868-8999-d734b322efc1" width="95%">
</p>

---

### ⚖️ Properties

Edit component masses while FusionToDescription automatically computes the corresponding inertia tensors.

<p align="center">
<img src="https://github.com/user-attachments/assets/20838993-53f1-423e-8d91-57416fa8c59b" width="95%">
</p>

---

### 🎮 Simulation

Configure simulation features including:

* Gazebo plugins
* ROS-GZ Bridge
* Sensors
* ROS 2 Control

<p align="center">
<img src="https://github.com/user-attachments/assets/ce7a0584-520b-4720-8a4d-b63445fea671" width="95%">
</p>

---

### ⚙️ Advanced

Additional export options for advanced ROS 2 workflows.

<p align="center">
<img src="https://github.com/user-attachments/assets/786cfe25-0585-4807-9189-20761f1086e6" width="95%">
</p>

---

## 📦 Export Result

A complete ROS 2 description package is generated automatically.

<p align="center">
<img src="https://github.com/user-attachments/assets/71ecfa46-278c-4e3f-9ab4-1984b865d32c" width="95%">
</p>

---

## 📁 Export Location

Generated packages are saved directly to the selected destination.

<p align="center">
<img src="https://github.com/user-attachments/assets/a2719525-de13-4f5d-835d-5cd502457a16" width="95%">
</p>

---

## 🚀 Release Highlights

* ✅ Fully functional FusionToDescription UI
* ✅ Complete ROS 2 description package generation
* ✅ Automatic inertia calculation
* ✅ Editable mass properties
* ✅ Mesh and primitive collision generation
* ✅ Gazebo plugin generation
* ✅ ROS-GZ Bridge configuration
* ✅ Sensor integration
* ✅ Optional ROS 2 Control support
* ✅ Xacro-based package structure
* ✅ Ready for ROS 2 simulation

---

## 🔜 Coming in the Next Release

Development is currently focused on polishing the generated ROS 2 description package.

Planned improvements include:

- ✅ Resolving the remaining syntax issues in the exported package
- 🎨 UI refinements and workflow enhancements
- ⚡ Improved export reliability and validation
- 🛠️ General bug fixes and performance improvements

Stay tuned for the next release!
