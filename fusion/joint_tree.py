"""Utilities for converting Fusion joint endpoints into a URDF tree."""

from collections import defaultdict, deque


def orient_joints(joints, preferred_root="base_link"):
    """Orient undirected Fusion joint endpoints away from a single root.

    Fusion's ``occurrenceOne`` and ``occurrenceTwo`` identify the two joint
    endpoints; they do not define a parent/child relationship.  URDF does,
    so the endpoints must be oriented as a tree before they are exported.

    The items in *joints* may be dictionaries or objects with ``parent`` and
    ``child`` attributes.  They are updated in place and returned.
    """
    if not joints:
        return joints

    def endpoints(joint):
        if isinstance(joint, dict):
            return joint.get("parent", ""), joint.get("child", "")
        return joint.parent, joint.child

    def set_endpoints(joint, parent, child):
        if isinstance(joint, dict):
            joint["parent"] = parent
            joint["child"] = child
        else:
            joint.parent = parent
            joint.child = child

    adjacency = defaultdict(list)
    valid_endpoints = set()

    for index, joint in enumerate(joints):
        first, second = endpoints(joint)
        if not first or not second:
            continue
        valid_endpoints.update((first, second))
        adjacency[first].append((index, second))
        adjacency[second].append((index, first))

    if not valid_endpoints:
        return joints

    # base_link is the conventional ROS root.  For models without one, keep a
    # uniquely implied Fusion direction when available, then fall back to a
    # stable endpoint so that the result is deterministic.
    if preferred_root in valid_endpoints:
        root = preferred_root
    else:
        raw_children = {
            second
            for joint in joints
            for _, second in (endpoints(joint),)
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

            visited_joints.add(index)
            set_endpoints(joints[index], parent, neighbour)

            if neighbour not in visited_links:
                visited_links.add(neighbour)
                queue.append(neighbour)

    # Disconnected joints are intentionally left in their original direction.
    # Validator reports the disconnected graph instead of silently inventing
    # additional roots.
    return joints
