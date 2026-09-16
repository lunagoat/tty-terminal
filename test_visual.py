#!/usr/bin/kitty +launch
"""Run the same renderer on XWayland so its own window can be captured by name."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import tty_terminal as app
original = app.engine_arguments
def arguments(args):
    argv = original(args)
    return [argv[0], '--override', 'linux_display_server=x11', *argv[1:]]
app.engine_arguments = arguments
app.main()
