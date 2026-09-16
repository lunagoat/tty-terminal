import contextlib
import hashlib
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fontTools.ttLib import TTFont
from build_font import build
from config import DEFAULTS, config_path, read_config
from tty_terminal import engine_arguments, parse_args


class Preferences(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'config.toml'

    def test_missing_config_and_xdg_path(self):
        self.assertEqual(read_config(self.path), DEFAULTS)
        with patch.dict(os.environ, {'XDG_CONFIG_HOME': self.temp.name}):
            self.assertEqual(config_path(), Path(self.temp.name) / 'tty-terminal/config.toml')

    def test_preferences_and_cli_precedence(self):
        self.path.write_text('columns=90\nrows=28\nfont_size=23\nfullscreen=true\ncursor_shape="block"\n')
        args = parse_args(['--config', str(self.path), '--windowed', '--columns', '101'])
        self.assertEqual((args.columns, args.rows, args.font_size, args.windowed), (101, 28, 23, True))
        argv = engine_arguments(args)
        self.assertIn('initial_window_width=101c', argv)
        self.assertIn('initial_window_height=28c', argv)
        self.assertIn('font_size=17.25', argv)
        self.assertIn('cursor_shape=block', argv)

    def test_invalid_settings_fail_before_launch(self):
        for text in ['rows=true', 'rows=0', 'font_size=65', 'font_size=7',
                     'cursor_shape="bad"', 'fullscreen="false"', 'typo=1', 'rows=']:
            with self.subTest(text=text):
                self.path.write_text(text)
                with self.assertRaises(ValueError):
                    read_config(self.path)

    def test_command_arguments_are_not_terminal_options(self):
        args = parse_args(['--config', str(self.path), '-e', 'printf', '--rows', '5'])
        self.assertEqual(args.command, ['printf', '--rows', '5'])
        self.assertEqual(args.rows, DEFAULTS['rows'])
        self.assertEqual(engine_arguments(args)[-3:], args.command)

    def test_cli_bounds(self):
        for option, value in [('--rows', '0'), ('--columns', '1001'), ('--font-size', '65')]:
            with self.subTest(option=option), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    parse_args(['--config', str(self.path), option, value])
                self.assertEqual(error.exception.code, 2)


class FontBuild(unittest.TestCase):
    def test_reproducible_font_with_console_metrics(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = (Path(directory) / name for name in ('one.ttf', 'two.ttf'))
            with patch.dict(os.environ, {'SOURCE_DATE_EPOCH': '0'}):
                build(None, first)
                build(None, second)
            self.assertEqual(hashlib.sha256(first.read_bytes()).digest(),
                             hashlib.sha256(second.read_bytes()).digest())
            with TTFont(first) as font:
                self.assertEqual(font['head'].unitsPerEm, 1024)
                cmap = font.getBestCmap()
                for character in 'AiMW0─│':
                    glyph = font['glyf'][cmap[ord(character)]]
                    advance, bearing = font['hmtx'][cmap[ord(character)]]
                    self.assertEqual(advance, 512)
                    self.assertEqual(bearing, getattr(glyph, 'xMin', 0))


if __name__ == '__main__':
    unittest.main()
