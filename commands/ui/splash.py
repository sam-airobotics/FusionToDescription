"""FusionToDescription startup splash palette."""

import os
import adsk.core

PALETTE_ID = "fusiontodescription_startup_splash"
PALETTE_NAME = "FusionToDescription"

SPLASH_DURATION_MS = 5000

_palette = None
_timer = None


def show(ui):
    """Show the logo centered on screen for five seconds."""
    global _palette, _timer

    if not ui:
        return

    try:
        if _palette:
            _palette.isVisible = True
            _start_timer()
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
            False,
            True,
            True,
            520,
            420,
        )

        # Let Fusion finish creating the palette, then center it.
        try:
            _palette.centered = True
        except Exception:
            pass

        _start_timer()

    except Exception:
        _palette = None


def _start_timer():
    """Start a five-second timer before the splash is hidden."""
    global _timer

    try:
        if _timer:
            _timer.stop()
            _timer.deleteMe()
    except Exception:
        pass

    try:
        _timer = adsk.core.TimerEventHandler()
        _timer.notify.add(_timer_notify)

        app = adsk.core.Application.get()
        if app:
            app.userInterface.events.add(_timer)
    except Exception:
        _timer = None


def _timer_notify(args):
    """Hide the splash after five seconds."""
    hide()


def hide():
    """Hide the startup splash before the main UI panel appears."""
    global _palette

    try:
        if _palette:
            _palette.isVisible = False
    except Exception:
        pass


def stop():
    """Remove the startup splash and timer."""
    global _palette, _timer

    try:
        if _timer:
            _timer.deleteMe()
    except Exception:
        pass

    try:
        if _palette:
            _palette.deleteMe()
    except Exception:
        pass

    _timer = None
    _palette = None
