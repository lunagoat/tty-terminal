# Third-party components

The MIT license applies to tty-terminal's original Python code, packaging,
documentation, and SVG icon. It does not relicense these components:

| Component | License | Source / notes |
| --- | --- | --- |
| `assets/font_8x16.c` | GPL-2.0-only | Linux kernel VGA 8×16 glyph data; its upstream SPDX label is `GPL-2.0`. https://github.com/torvalds/linux/blob/master/lib/fonts/font_8x16.c |
| `assets/unicode-map.json` | GPL-2.0-only | Unicode-to-glyph mapping extracted from kbd's `default8x16.psfu.gz`, preserving the existing font mapping. https://git.kernel.org/pub/scm/linux/kernel/git/legion/kbd.git/ |
| Generated `assets/tty-console.ttf` | GPL-2.0-only | Generated from the two assets above using `build_font.py`; complete source is in this repository. See `assets/FONT-LICENSE.txt`. |
| Kitty | GPL-3.0-only | External runtime dependency for the native package. https://github.com/kovidgoyal/kitty |

Kitty and other runtime libraries are **not** included in the native source
archive or AUR package. Their own packages supply them and their licenses.

The experimental local AppImage bundles third-party runtimes. Before publicly
redistributing that binary, provide the exact corresponding sources and notices
for those bundled components as required by their respective licenses. A copy
of installed license texts alone is not a complete corresponding-source bundle.
The source release workflow deliberately does not upload the local AppImage.
