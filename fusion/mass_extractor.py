"""Extract Fusion component masses in kilograms."""

import adsk.core

from ..utils.logger import Logger


def get_mass_data():
    app = adsk.core.Application.get()
    design = app.activeProduct
    if not design:
        return []

    data = []
    for occ in design.rootComponent.allOccurrences:
        try:
            component = occ.component
            mass = max(float(component.physicalProperties.mass), 0.0)
        except Exception as exc:
            Logger.warning(f"Failed to extract mass for '{getattr(component, 'name', '<unknown>')}': {exc}. Using 1.0 kg.")
            mass = 1.0
        data.append({"name": component.name, "mass": round(mass, 6)})
    return data
