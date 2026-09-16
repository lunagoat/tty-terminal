"""Set paths only for the bundled GUI; preserve the user's shell environment."""
import os
from pathlib import Path
import sys

app = Path(__file__).resolve().parent
usr = app.parents[1]
original = dict(os.environ)
# AppImage's portable config must not replace fish/KDE settings in child shells.
if os.environ.get('APPIMAGE') and Path(os.environ['APPIMAGE'] + '.config').is_dir():
    original.pop('XDG_CONFIG_HOME', None)
for key in ('APPIMAGE', 'APPDIR', 'ARGV0', 'APPIMAGE_EXTRACT_AND_RUN'):
    original.pop(key, None)
sys.path.insert(0, str(usr / 'lib/kitty'))
sys.kitty_run_data = {'bundle_exe_dir': str(usr / 'bin'),
                     'config_dir': str(Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))) / 'tty-terminal')}
sys.path.insert(0, str(app))
import tty_terminal
# Preserve portable config for tty-terminal's parser, but restore the host's
# XDG config path before Kitty starts the user's shell.
saved_parse = tty_terminal.parse_args
def parse_then_restore(argv=None):
    args = saved_parse(argv)
    os.environ.clear()
    os.environ.update(original)
    return args
tty_terminal.parse_args = parse_then_restore
sys.exit(tty_terminal.main())
