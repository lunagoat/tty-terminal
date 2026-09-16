"""Validated TOML preferences; no graphical dependencies."""
import os
from pathlib import Path
import tomllib

DEFAULTS = dict(columns=120, rows=40, fullscreen=False, font_size=16,
                scrollback_lines=10000, cursor_shape='underline',
                cursor_blink=True, audible_bell=False, decorated=False,
                directory='')


def config_path():
    return Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config') / 'tty-terminal/config.toml'


def read_config(path):
    settings = DEFAULTS.copy()
    try:
        with Path(path).open('rb') as stream:
            values = tomllib.load(stream)
    except FileNotFoundError:
        return settings
    unknown = values.keys() - settings.keys()
    if unknown:
        raise ValueError(f'Unknown config setting(s): {", ".join(sorted(unknown))}')
    for key, value in values.items():
        if type(value) is not type(settings[key]):
            raise ValueError(f'{key} must be {type(settings[key]).__name__}')
    settings.update(values)
    for key, low, high in [('columns', 2, 1000), ('rows', 2, 1000),
                           ('scrollback_lines', 0, 1000000)]:
        if not low <= settings[key] <= high:
            raise ValueError(f'{key} must be between {low} and {high}')
    if not 8 <= settings['font_size'] <= 64:
        raise ValueError('font_size must be between 8 and 64')
    if settings['cursor_shape'] not in ('underline', 'block', 'ibeam'):
        raise ValueError('cursor_shape must be underline, block, or ibeam')
    return settings
