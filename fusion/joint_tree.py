"""Utilities for converting Fusion joint endpoints into a URDF tree."""

from collections import defaultdict, deque


def _endpoints(joint):
    if isinstance(joint, dict):
        return joint.get("parent", ""), joint.get("child", "")
    return joint.parent, joint.child


def _set_endpoints(joint, parent, child):
    if isinstance(joint, dict):
        joint["parent"] = parent
        joint["child"] = child
    else:
        joint.parent = parent
        joint.child = child


def _swap_frame_data(joint):
    """Swap endpoint frames and invert motion when a joint is reversed."""
    if isinstance(joint, dict):
        joint["_parent_frame"], joint["_child_frame"] = joint.get("_child_frame"), joint.get("_parent_frame")
        joint_type = joint.get("type")
        if joint_type in ("revolute", "prismatic"):
            axis = joint.get("_axis_world")
            if axis is not None:
                joint["_axis_world"] = {"x": -axis["x"], "y": -axis["y"], "z": -axis["z"]}
            limits = joint.get("limits") or {}
            if "lower" in limits and "upper" in limits:
                lower, upper = float(limits["lower"]), float(limits["upper"])
                joint["limits"] = {**limits, "lower": -upper, "upper": -lower}
        return

    if hasattr(joint, "parent_frame") and hasattr(joint, "child_frame"):
        joint.parent_frame, joint.child_frame = joint.child_frame, joint.parent_frame

    joint_type = getattr(joint, "joint_type", "")
    if joint_type in ("revolute", "prismatic") and hasattr(joint, "axis"):
        axis = joint.axis or {}
        joint.axis = {"x": -float(axis.get("x", 0.0)), "y": -float(axis.get("y", 0.0)), "z": -float(axis.get("z", 1.0))}
        limits = joint.limits or {}
        if "lower" in limits and "upper" in limits:
            lower, upper = float(limits["lower"]), float(limits["upper"])
            joint.limits = {**limits, "lower": -upper, "upper": -lower}


def orient_joints(joints, preferred_root="base_link"):
    """Orient Fusion joint endpoints away from one URDF root."""
    if not joints:
        return joints

    adjacency = defaultdict(list)
    valid_endpoints = set()
    for index, joint in enumerate(joints):
        first, second = _endpoints(joint)
        if not first or not second:
            continue
        valid_endpoints.update((first, second))
        adjacency[first].append((index, second))
        adjacency[second].append((index, first))

    if not valid_endpoints:
        return joints

    if preferred_root in valid_endpoints:
        root = preferred_root
    else:
        raw_children = {
            second
            for joint in joints
            for _, second in [_endpoints(joint)]
            if second
        }
        implied_roots = sorted(valid_endpoints - raw_children)
        root = implied_roots[0] if len(implied_roots) == 1 else sorted(valid_endpoints)[0]

    visited_links = {root}
    visited_joints = set()
    queue = deque([root])

    while queue:
        parent = queue.popleft()
        for index, neighbour in adjacency[parent]:
            if index in visited_joints:
                continue
            joint = joints[index]
            old_parent, _ = _endpoints(joint)
            if old_parent != parent:
                _swap_frame_data(joint)
            _set_endpoints(joint, parent, neighbour)
            visited_joints.add(index)
            if neighbour not in visited_links:
                visited_links.add(neighbour)
                queue.append(neighbour)

    return joints
