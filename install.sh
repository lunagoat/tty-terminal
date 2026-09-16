#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
/usr/bin/python -c 'import fontTools; import shutil; assert shutil.which("kitty")' || {
    echo 'Install dependencies: sudo pacman -S kitty python-fonttools' >&2
    exit 1
}
/usr/bin/python "$project_dir/build_font.py" "$project_dir/assets/tty-console.ttf"
mkdir -p "$HOME/.local/bin" "$HOME/.local/share/applications"
config_dir="${XDG_CONFIG_HOME:-$HOME/.config}/tty-terminal"
mkdir -p "$config_dir"
if [[ ! -e "$config_dir/config.toml" ]]; then
    cp "$project_dir/config.example.toml" "$config_dir/config.toml"
fi
chmod +x "$project_dir/tty_terminal.py"
ln -sfn "$project_dir/tty_terminal.py" "$HOME/.local/bin/tty-terminal"
cat > "$HOME/.local/share/applications/tty-terminal.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=TTY Terminal
Comment=A terminal with the classic Linux console appearance
Exec="$HOME/.local/bin/tty-terminal"
Icon=utilities-terminal
Terminal=false
Categories=System;TerminalEmulator;
StartupWMClass=tty-terminal
Keywords=console;shell;tty;
EOF
echo 'Installed TTY Terminal. Launch from the application menu or ~/.local/bin/tty-terminal.'
