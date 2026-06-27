import adsk.core
import traceback
from ..utils.logger import Logger


def get_mass_data():
    """Extract mass data from all Fusion components.
    
    Returns:
        List of dicts with component name and mass (kg)
        
    Raises:
        RuntimeError if mass data cannot be extracted
    """
    app = adsk.core.Application.get()

    design = app.activeProduct

    data = []

    if not design:
        return data

    root = design.rootComponent

    for occ in root.occurrences:

        component = occ.component

        try:
            physical = component.physicalProperties
            mass = physical.mass
        except Exception as e:
            Logger.warning(
                f"Failed to extract mass for '{component.name}': {str(e)}. Using default 1.0 kg."
            )
            mass = 1.0

        data.append({

            "name": component.name,

            "mass": round(
                mass,
                4
            )

        })

    return data