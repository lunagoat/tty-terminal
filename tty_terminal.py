#!/usr/bin/python
"""TTY-styled terminal powered by Kitty, with native inline images."""
import argparse
import ctypes
import os
from pathlib import Path
import pwd
import shutil
import sys

ROOT = Path(__file__).resolve().parent
VERSION = (ROOT / 'VERSION').read_text().strip() if (ROOT / 'VERSION').exists() else '0.1.0'
sys.path.insert(0, str(ROOT))
from config import config_path, read_config

PALETTE = ('#000000', '#aa0000', '#00aa00', '#aa5500',
           '#0000aa', '#aa00aa', '#00aaaa', '#aaaaaa',
           '#555555', '#ff5555', '#55ff55', '#ffff55',
           '#5555ff', '#ff55ff', '#55ffff', '#ffffff')


def set_process_name():
    libc = ctypes.CDLL(None, use_errno=True)
    libc.prctl.argtypes = [ctypes.c_int, ctypes.c_char_p,
                          ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]
    libc.prctl.restype = ctypes.c_int
    if libc.prctl(15, b'tty-terminal', 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), 'Unable to set terminal process name')


def register_font():
    font = ROOT / 'assets/tty-console.ttf'
    fc = ctypes.CDLL('libfontconfig.so.1')
    fc.FcConfigGetCurrent.restype = ctypes.c_void_p
    fc.FcConfigAppFontAddFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    fc.FcConfigAppFontAddFile.restype = ctypes.c_int
    fc.FcConfigParseAndLoadFromMemory.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    fc.FcConfigParseAndLoadFromMemory.restype = ctypes.c_int
    config = fc.FcConfigGetCurrent()
    if not fc.FcConfigAppFontAddFile(config, os.fsencode(font)):
        raise RuntimeError('Console font missing. Run ./install.sh first.')
    rules = b'''<?xml version="1.0"?><fontconfig>
      <match target="font"><test name="family"><string>TTY Console</string></test>
      <edit name="antialias" mode="assign"><bool>false</bool></edit>
      <edit name="hinting" mode="assign"><bool>false</bool></edit>
      <edit name="embolden" mode="assign"><bool>false</bool></edit>
      </match></fontconfig>'''
    if not fc.FcConfigParseAndLoadFromMemory(config, rules, True):
        raise RuntimeError('Could not configure console font rendering')


def engine_arguments(args):
    opts = {
        'font_family': 'family="TTY Console" style="Regular"',
        'bold_font': 'family="TTY Console" style="Regular"',
        'italic_font': 'family="TTY Console" style="Regular"',
        'bold_italic_font': 'family="TTY Console" style="Regular"',
        'font_size': str(args.font_size * 0.75),
        'disable_ligatures': 'always',
        'foreground': '#aaaaaa', 'background': '#000000', 'cursor': '#aaaaaa',
        'cursor_shape': {'ibeam': 'beam'}.get(args.cursor_shape, args.cursor_shape),
        'cursor_blink_interval': '0.5' if args.cursor_blink else '0',
        'cursor_stop_blinking_after': '0', 'cursor_trail': '0',
        'enable_audio_bell': 'yes' if args.audible_bell else 'no',
        'scrollback_lines': str(args.scrollback_lines),
        'hide_window_decorations': 'no' if args.decorated else 'yes',
        'initial_window_width': f'{args.columns}c',
        'initial_window_height': f'{args.rows}c',
        'remember_window_size': 'no', 'window_padding_width': '0',
        'window_margin_width': '0', 'window_border_width': '0',
        'placement_strategy': 'top-left', 'tab_bar_style': 'hidden',
        'background_opacity': '1', 'text_composition_strategy': 'legacy',
        'shell_integration': 'disabled', 'confirm_os_window_close': '0',
        'clear_all_shortcuts': 'yes', 'allow_remote_control': 'no',
    }
    opts.update({f'color{i}': value for i, value in enumerate(PALETTE)})
    argv = ['tty-terminal', '--config', 'NONE', '--class', 'tty-terminal',
            '--title', 'tty-terminal', '--directory', args.directory,
            '--start-as', 'normal' if args.windowed else 'fullscreen']
    for key, value in opts.items():
        argv.extend(['--override', f'{key}={value}'])
    for shortcut, action in [
        ('f11', 'toggle_fullscreen'), ('ctrl+shift+c', 'copy_to_clipboard'),
        ('ctrl+shift+v', 'paste_from_clipboard'), ('ctrl+shift+q', 'close_os_window'),
        ('ctrl+shift+plus', 'change_font_size all +0.75'),
        ('ctrl+shift+equal', 'change_font_size all +0.75'),
        ('ctrl+shift+minus', 'change_font_size all -0.75'),
        ('shift+page_up', 'scroll_page_up'), ('shift+page_down', 'scroll_page_down')]:
        argv.extend(['--override', f'map={shortcut} {action}'])
    argv.extend(['--override', 'env=TERM_PROGRAM=tty-terminal'])
    argv.extend(args.command or [pwd.getpwuid(os.getuid()).pw_shell or '/bin/bash'])
    return argv


def parse_args(argv=None):
    parser = argparse.ArgumentParser(prog='tty-terminal', description=__doc__)
    parser.add_argument('--version', action='version', version=f'tty-terminal {VERSION}')
    parser.add_argument('--config', type=Path, default=config_path(), help='TOML preferences file')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--windowed', action='store_true', default=None, help='Start in a window')
    modes.add_argument('--fullscreen', dest='windowed', action='store_false', default=None, help='Start fullscreen')
    parser.add_argument('--columns', type=int, help='Initial window width in characters')
    parser.add_argument('--rows', type=int, help='Initial window height in characters')
    parser.add_argument('--font-size', type=int,
                        help='Console font height in logical pixels, 8–64 (default: 16)')
    parser.add_argument('--directory', help='Initial working directory')
    parser.add_argument('-e', '--command', nargs=argparse.REMAINDER, help='Command and arguments to run')
    args = parser.parse_args(argv)
    try:
        settings = read_config(args.config)
    except (OSError, ValueError) as error:
        parser.error(f'{args.config}: {error}')
    if args.windowed is None:
        args.windowed = not settings['fullscreen']
    for key, value in settings.items():
        if key != 'fullscreen' and getattr(args, key, None) is None:
            setattr(args, key, value)
    for key in ('columns', 'rows'):
        if not 2 <= getattr(args, key) <= 1000:
            parser.error(f'--{key} must be between 2 and 1000')
    args.directory = args.directory or os.getcwd()
    if not 8 <= args.font_size <= 64:
        parser.error('--font-size must be between 8 and 64')
    args.directory = os.path.abspath(os.path.expanduser(args.directory))
    if not os.path.isdir(args.directory):
        parser.error(f'Not a directory: {args.directory}')
    return args


def main():
    args = parse_args()
    try:
        import kitty.fast_data_types
    except ImportError:
        engine = shutil.which('kitty')
        if not engine:
            raise SystemExit('Kitty is required. Install it with: sudo pacman -S kitty')
        os.execv(engine, [engine, '+launch', str(ROOT / 'tty_terminal.py'), *sys.argv[1:]])
    set_process_name()
    register_font()
    sys.argv = engine_arguments(args)
    # +launch's parsed CLI flags must not override our generated options.
    getattr(sys, 'kitty_run_data', {}).pop('cli_flags', None)
    from kitty.main import main as kitty_main
    kitty_main()
    return 0


if __name__ == '__main__':
    sys.exit(main())
