"""FusionToDescription startup splash palette."""

import os
import adsk.core

PALETTE_ID = "fusiontodescription_startup_splash"
PALETTE_NAME = "FusionToDescription"

_palette = None


def show(ui):
    """Show the FusionToDescription logo before the export dialog opens."""
    global _palette

    if not ui:
        return

    try:
        if _palette:
            _palette.isVisible = True
            return

        resources_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "resources")
        )
        splash_url = "file:///" + os.path.join(
            resources_dir, "splash.html"
        ).replace("\\", "/")

        _palette = ui.palettes.add(
            PALETTE_ID,
            PALETTE_NAME,
            splash_url,
            True,
            False,
            False,
            420,
            320,
        )
    except Exception:
        _palette = None


def hide():
    """Hide the startup splash when the export dialog is about to open."""
    global _palette

    try:
        if _palette:
            _palette.isVisible = False
    except Exception:
        pass


def stop():
    """Remove the startup splash palette."""
    global _palette

    try:
        if _palette:
            _palette.deleteMe()
    except Exception:
        pass

    _palette = None
