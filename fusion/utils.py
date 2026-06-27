"""
utils.py

Common Fusion 360 utility functions used throughout the
FusionToDescription exporter.
"""

import math
import re

import adsk.core
import adsk.fusion


# ==========================================================
# Name Utilities
# ==========================================================

def sanitize_name(name: str) -> str:
    """
    Convert a Fusion component name into a ROS-compatible name.
    """

    name = name.strip().lower()
    name = name.replace(" ", "_")
    name = re.sub(r"[^a-zA-Z0-9_]", "", name)

    return name


# ==========================================================
# Unit Conversion
# ==========================================================

def cm_to_m(value: float) -> float:
    """Fusion default units (cm) -> meters"""
    return value / 100.0


def mm_to_m(value: float) -> float:
    return value / 1000.0


def deg_to_rad(value: float) -> float:
    return math.radians(value)


# ==========================================================
# Matrix Utilities
# ==========================================================

def get_translation(matrix):

    translation = matrix.translation

    return {
        "x": translation.x,
        "y": translation.y,
        "z": translation.z
    }


def get_rotation_matrix(matrix):

    return [

        [
            matrix.getCell(0, 0),
            matrix.getCell(0, 1),
            matrix.getCell(0, 2)
        ],

        [
            matrix.getCell(1, 0),
            matrix.getCell(1, 1),
            matrix.getCell(1, 2)
        ],

        [
            matrix.getCell(2, 0),
            matrix.getCell(2, 1),
            matrix.getCell(2, 2)
        ]
    ]


def matrix_to_rpy(matrix):
    """
    Convert a Fusion Matrix3D rotation matrix into
    Roll-Pitch-Yaw angles (radians).
    """

    r11 = matrix.getCell(0, 0)
    r21 = matrix.getCell(1, 0)
    r31 = matrix.getCell(2, 0)
    r32 = matrix.getCell(2, 1)
    r33 = matrix.getCell(2, 2)

    pitch = math.atan2(-r31, math.sqrt(r11**2 + r21**2))

    roll = math.atan2(r32, r33)

    yaw = math.atan2(r21, r11)

    return {
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw
    }


# ==========================================================
# Fusion Helpers
# ==========================================================

def get_root_component(design):

    if not isinstance(design, adsk.fusion.Design):
        return None

    return design.rootComponent


def get_all_occurrences(root):

    return list(root.occurrences)


def get_component_by_name(root, name):

    for occ in root.occurrences:

        if occ.component.name == name:
            return occ

    return None


# ==========================================================
# Bounding Box
# ==========================================================

def bounding_box_dimensions(body):

    box = body.boundingBox

    return {

        "length": abs(box.maxPoint.x - box.minPoint.x),

        "breadth": abs(box.maxPoint.y - box.minPoint.y),

        "height": abs(box.maxPoint.z - box.minPoint.z)

    }


# ==========================================================
# Physical Properties
# ==========================================================

def get_mass(component):

    try:
        return component.physicalProperties.mass
    except Exception as e:
        # Return default mass if extraction fails
        return 0.0


def get_center_of_mass(component):

    try:

        com = component.physicalProperties.centerOfMass

        return {

            "x": com.x,
            "y": com.y,
            "z": com.z

        }

    except Exception as e:
        # Return default center of mass if extraction fails
        return {

            "x": 0.0,
            "y": 0.0,
            "z": 0.0

        }


# ==========================================================
# Geometry Utilities
# ==========================================================

def is_visible(occurrence):

    try:
        return occurrence.isLightBulbOn

    except Exception as e:
        # Default to visible if cannot determine
        return False


def has_bodies(component):

    return component.bRepBodies.count > 0


# ==========================================================
# File Utilities
# ==========================================================

def mesh_filename(component_name):

    return f"{sanitize_name(component_name)}.stl"


def package_uri(package_name, mesh_name):

    return f"package://{package_name}/meshes/{mesh_name}"