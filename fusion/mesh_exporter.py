import os
import traceback

import adsk.core
import adsk.fusion


app = adsk.core.Application.get()


def _sanitize_name(value):
    result = str(value or "")
    for char in ("/", "\\", " ", ":", "-", "."):
        result = result.replace(char, "_")
    while "__" in result:
        result = result.replace("__", "_")
    result = result.strip("_") or "unnamed"
    if not result[0].isalpha():
        result = f"link_{result}"
    return result


class MeshExporter:
    """Export meshes using the same occurrence-based names as RobotModel links."""

    def __init__(self, export_directory):
        self.export_directory = export_directory
        self.design = app.activeProduct
        if not isinstance(self.design, adsk.fusion.Design):
            raise RuntimeError("No active Fusion Design.")
        self.export_manager = self.design.exportManager
        self.root = self.design.rootComponent
        os.makedirs(self.export_directory, exist_ok=True)

    def export_all(self):
        exported = []
        for occ in self.root.allOccurrences:
            try:
                component = occ.component
                if component.bRepBodies.count == 0:
                    continue
                if not occ.isLightBulbOn or occ.childOccurrences.count > 0:
                    continue
                if occ.component.joints.count > 0:
                    continue
                path = self.export_component(occ)
                exported.append(path)
            except Exception as exc:
                print(f"Error exporting mesh for {getattr(occ.component, 'name', '<unknown>')}: {exc}")
                print(traceback.format_exc())
        return exported

    def export_component(self, occurrence):
        component = occurrence.component
        link_name = "base_link" if component.name == "base_link" else _sanitize_name(occurrence.fullPathName)
        filename = f"{link_name}.stl"
        filepath = os.path.join(self.export_directory, filename)

        options = self.export_manager.createSTLExportOptions(occurrence, filepath)
        options.sendToPrintUtility = False
        options.isBinaryFormat = True
        options.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        self.export_manager.execute(options)

        if not os.path.isfile(filepath):
            raise RuntimeError(f"Fusion did not create the expected mesh file: {filepath}")
        return filepath
