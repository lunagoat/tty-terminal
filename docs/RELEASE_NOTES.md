First public release of tty-terminal: a Linux console-styled frontend to Kitty.

- VGA console font and palette, borderless windows, and fullscreen toggle.
- Native Kitty image support (`kitten icat image.png`).
- TOML preferences and command-line overrides.
- Requires Python 3.11+, Kitty 0.48.2+, and Fontconfig.

The source archive includes the complete font sources and native installation
support. Build requirements: Make, Python FontTools, and desktop-file-utils for
the checks. See README.md for installation and configuration.

The AUR package is prepared separately; do not assume it has been published.
The experimental CachyOS AppImage is not included in this public source release.
