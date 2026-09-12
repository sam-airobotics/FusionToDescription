"""Validation utilities for the FusionToDescription export pipeline."""

import math
import os
import re


class Validator:
    def __init__(self, config, robot=None):
        self.config = config
        self.robot = robot
        self.errors = []
        self.warnings = []

    def validate(self):
        self.errors.clear()
        self.warnings.clear()
        self._validate_config()
        if self.robot is not None:
            self._validate_robot()
        return {"valid": not self.errors, "errors": list(self.errors), "warnings": list(self.warnings)}

    def _validate_config(self):
        if not self.config.robot_name or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", self.config.robot_name):
            self.errors.append("Robot name must start with a letter and contain only letters, numbers, and underscores.")
        if not re.fullmatch(r"[a-z][a-z0-9_]*", self.config.package_name):
            self.errors.append("ROS package name must start with a lowercase letter and contain only lowercase letters, numbers, and underscores.")
        if not self.config.export_directory:
            self.errors.append("Export directory is not specified.")
        if self.config.mesh_format.lower() not in ("stl", "obj"):
            self.errors.append(f"Unsupported mesh format: {self.config.mesh_format}")

    def _validate_robot(self):
        self._validate_links()
        self._validate_joints()

    def _validate_links(self):
        if not self.robot.links:
            self.errors.append("No links were found.")
            return
        names = set()
        for link in self.robot.links:
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", link.name):
                self.errors.append(f"Invalid link name '{link.name}'.")
            if link.name in names:
                self.errors.append(f"Duplicate link: {link.name}")
            names.add(link.name)
            if link.mass <= 0:
                self.warnings.append(f"Non-positive mass for link {link.name}; a small fallback may be used.")
            if not link.mesh:
                self.warnings.append(f"No mesh assigned to {link.name}")
            for key in ("ixx", "iyy", "izz"):
                value = float(link.inertia.get(key, 0.0))
                if not math.isfinite(value) or value <= 0:
                    self.errors.append(f"Link '{link.name}' has invalid {key} inertia: {value}.")

    def _validate_joints(self):
        names = set()
        link_names = {link.name for link in self.robot.links}
        child_joints = {}
        adjacency = {name: [] for name in link_names}

        for joint in self.robot.joints:
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", joint.name):
                self.errors.append(f"Invalid joint name '{joint.name}'.")
            if joint.name in names:
                self.errors.append(f"Duplicate joint: {joint.name}")
            names.add(joint.name)
            if joint.parent not in link_names:
                self.errors.append(f"Joint '{joint.name}' references unknown parent '{joint.parent}'.")
            if joint.child not in link_names:
                self.errors.append(f"Joint '{joint.name}' references unknown child '{joint.child}'.")
            if joint.parent == joint.child:
                self.errors.append(f"Joint '{joint.name}' connects a link to itself.")
                continue
            if joint.child in child_joints:
                self.errors.append(
                    f"Link '{joint.child}' has multiple parent joints: '{child_joints[joint.child]}' and '{joint.name}'."
                )
            else:
                child_joints[joint.child] = joint.name
            if joint.parent in adjacency and joint.child in link_names:
                adjacency[joint.parent].append(joint.child)

            if joint.joint_type in ("revolute", "prismatic"):
                limits = joint.limits or {}
                if limits:
                    if float(limits.get("lower", 0.0)) > float(limits.get("upper", 0.0)):
                        self.errors.append(f"Joint '{joint.name}' has lower limit greater than upper limit.")
                elif joint.joint_type == "revolute":
                    self.warnings.append(f"Revolute joint '{joint.name}' is unbounded; no <limit> will be emitted.")

        roots = sorted(link_names - set(child_joints))
        if len(roots) != 1:
            self.errors.append(
                "Robot links must form one URDF tree; "
                f"found {len(roots)} root links: {', '.join(roots) if roots else 'none'}."
            )
            return
        reachable = set()
        stack = [roots[0]]
        while stack:
            link = stack.pop()
            if link in reachable:
                continue
            reachable.add(link)
            stack.extend(adjacency.get(link, []))
        disconnected = sorted(link_names - reachable)
        if disconnected:
            self.errors.append(f"Links are disconnected from root '{roots[0]}': {', '.join(disconnected)}.")

    def is_valid(self):
        return not self.errors

    def print_report(self):
        print("\n========== Validation Report ==========\n")
        if self.errors:
            print("Errors:")
            for error in self.errors:
                print(f"  ✗ {error}")
        else:
            print("No validation errors.")
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  ! {warning}")
        print("\n=======================================\n")
