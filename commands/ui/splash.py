"""FusionToDescription startup splash palette."""

import os
import sys
import adsk.core

PALETTE_ID = "fusiontodescription_startup_splash"
PALETTE_NAME = "FusionToDescription"

_palette = None


def _screen_size():
    """Return the primary screen size in pixels when available."""
    if sys.platform.startswith("win"):
        try:
            import ctypes
            user32 = ctypes.windll.user32
            return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        except Exception:
            pass

    return 1920, 1080


def show(ui):
    """Show a small centered startup window containing the logo."""
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

        # Keep the splash intentionally small and centered.
        width = 360
        height = 260

        screen_width, screen_height = _screen_size()
        left = max(0, int((screen_width - width) / 2))
        top = max(0, int((screen_height - height) / 2))

        # Create hidden first so the window is positioned before it becomes
        # visible. The actual exporter command remains separate.
        _palette = ui.palettes.add(
            PALETTE_ID,
            PALETTE_NAME,
            splash_url,
            False,
            False,
            False,
            width,
            height,
        )

        if _palette:
            _palette.setPosition(left, top)
            _palette.isVisible = True

    except Exception:
        _palette = None


def hide():
    """Hide the startup splash."""
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
