#!/usr/bin/python
"""Turn the system's 8-pixel-wide PSF console font into square TrueType outlines."""
import gzip
import struct
import re
import json
import os
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen


def build(source, target):
    if source is None:
        mapping = json.loads((Path(__file__).parent / 'assets/unicode-map.json').read_text())
        cmap = {int(code): f'g{index}' for code, index in mapping.items()}
        height, count = 16, 256
    else:
        data = gzip.decompress(Path(source).read_bytes())
        cmap = {}
        if data[:4] == b'\x72\xb5\x4a\x86':
            _, _, start, flags, count, charsize, height, width = struct.unpack('<8I', data[:32])
            if width != 8 or charsize != height:
                raise ValueError('Expected an 8-pixel-wide font')
            if flags & 1:
                table = data[start + count * charsize:]
                for index, entry in enumerate(table.split(b'\xff')[:count]):
                    for character in entry.split(b'\xfe')[0].decode('utf-8'):
                        cmap.setdefault(ord(character), f'g{index}')
        elif data[:2] == b'\x36\x04':
            mode, height = data[2:4]
            count = 512 if mode & 1 else 256
            start = 4
            if mode & 6:
                index, sequence = 0, False
                for (code,) in struct.iter_unpack('<H', data[start + count * height:]):
                    if code == 0xFFFF:
                        index += 1
                        sequence = False
                    elif code == 0xFFFE:
                        sequence = True
                    elif not sequence and index < count:
                        cmap.setdefault(code, f'g{index}')
        else:
            raise ValueError('Expected a PSF1 or PSF2 console font')
        if not cmap:
            cmap = {ord(bytes([i]).decode('cp437')): f'g{i}' for i in range(256)}
    # kbd's default8x16 is similar to, but not identical to, the kernel VGA font.
    kernel_source = Path(__file__).parent / 'assets' / 'font_8x16.c'
    bitmap = bytes(int(value, 16) for value in re.findall(
        r'^\s*(0x[0-9a-fA-F]{2}),', kernel_source.read_text(), re.MULTILINE))
    if height != 16 or count != 256 or len(bitmap) != count * height:
        raise ValueError('Expected the kernel VGA 8x16 font with 256 glyphs')
    scale = 64
    glyphs = {'.notdef': TTGlyphPen(None).glyph()}
    for i in range(count):
        pen = TTGlyphPen(None)
        for y, row in enumerate(bitmap[i * height:(i + 1) * height]):
            for x in range(8):
                if row & (128 >> x):
                    left, bottom = x * scale, (height - y - 3) * scale
                    pen.moveTo((left, bottom))
                    pen.lineTo((left, bottom + scale))
                    pen.lineTo((left + scale, bottom + scale))
                    pen.lineTo((left + scale, bottom))
                    pen.closePath()
        glyphs[f'g{i}'] = pen.glyph()
    fb = FontBuilder(height * scale, isTTF=True)
    fb.setupGlyphOrder(list(glyphs))
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    # Preserve each bitmap's left padding, including narrow glyphs such as 'i'.
    fb.setupHorizontalMetrics({name: (8 * scale, getattr(glyph, 'xMin', 0))
                               for name, glyph in glyphs.items()})
    fb.setupHorizontalHeader(ascent=(height - 2) * scale, descent=-2 * scale, lineGap=0)
    fb.setupNameTable({'familyName': 'TTY Console', 'styleName': 'Regular',
                       'uniqueFontIdentifier': 'TTYConsole-SystemPSF',
                       'fullName': 'TTY Console', 'psName': 'TTYConsole',
                       'version': 'Version 1.0',
                       'licenseDescription': 'GPL-2.0-only; see assets/FONT-LICENSE.txt',
                       'licenseInfoURL': 'https://www.gnu.org/licenses/old-licenses/gpl-2.0.html'})
    fb.setupOS2(sTypoAscender=(height - 2) * scale, sTypoDescender=-2 * scale,
                sTypoLineGap=0, usWinAscent=(height - 2) * scale,
                usWinDescent=2 * scale, fsSelection=0x40)
    fb.setupPost(isFixedPitch=1)
    fb.setupMaxp()
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    epoch = int(os.environ.get('SOURCE_DATE_EPOCH', '0')) + 2082844800
    fb.font['head'].created = fb.font['head'].modified = epoch
    fb.font.recalcTimestamp = False
    fb.save(str(target))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', nargs='?', help='Optional PSF mapping override; bundled mapping is the default')
    parser.add_argument('target')
    args = parser.parse_args()
    build(args.source, args.target)
