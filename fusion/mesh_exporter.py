import os
import traceback
import adsk.core
import adsk.fusion


app = adsk.core.Application.get()


class MeshExporter:

    def __init__(self, export_directory):

        self.export_directory = export_directory

        self.design = app.activeProduct

        if not isinstance(self.design, adsk.fusion.Design):
            raise RuntimeError("No active Fusion Design.")

        self.export_manager = self.design.exportManager

        self.root = self.design.rootComponent

    # ---------------------------------------------------------
    # Export Complete Robot
    # ---------------------------------------------------------

    def export_all(self):

        exported = []

        for occ in self.root.occurrences:

            try:

                path = self.export_component(occ)

                exported.append(path)

            except Exception as e:
                print(f"Error exporting mesh for {occ.component.name}: {str(e)}")
                print(traceback.format_exc())

        return exported

    # ---------------------------------------------------------
    # Export Single Component
    # ---------------------------------------------------------

    def export_component(self, occurrence):

        component = occurrence.component

        filename = f"{component.name}.stl"

        filepath = os.path.join(
            self.export_directory,
            filename
        )

        options = self.export_manager.createSTLExportOptions(
            occurrence,
            filepath
        )

        # High quality mesh

        options.meshRefinement = (
            adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        )

        self.export_manager.execute(options)

        return filepath