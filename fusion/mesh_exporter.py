"""Export Fusion occurrences as ROS mesh resources."""

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
    """Export meshes with the exact occurrence-derived names used by RobotModel."""

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
        failures = []
        for occurrence in self.root.allOccurrences:
            try:
                if not self._is_exportable(occurrence):
                    continue
                exported.append(self.export_component(occurrence))
            except Exception as exc:
                name = getattr(getattr(occurrence, "component", None), "name", "<unknown>")
                failures.append(f"{name}: {exc}")
                print(f"Error exporting mesh for {name}: {exc}")
                print(traceback.format_exc())
        if failures:
            raise RuntimeError("Mesh export failed:\n" + "\n".join(failures))
        return exported

    @staticmethod
    def _is_exportable(occurrence):
        component = occurrence.component
        return (
            component.bRepBodies.count > 0
            and occurrence.isLightBulbOn
            and occurrence.childOccurrences.count == 0
            and component.joints.count == 0
        )

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
        if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
            raise RuntimeError(f"Fusion did not create a valid mesh file: {filepath}")
        return filepath
