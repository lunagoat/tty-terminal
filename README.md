this is all vibecoded as fuck i dont know how it works. use at your own risk 👍

terminal emulator for linux systems that emulates a TTY interface

Appimage installation:
```sh
  chmod +x tty-terminal-x86_64.AppImage
  ./tty-terminal-x86_64.AppImage
```

AUR (wip)
```sh
yay -S tty-terminal
```

from source:
```sh
git clone https://github.com/lunagoat/tty-terminal.git
cd tty-terminal
make
sudo make PREFIX=/usr/local install
```

config:
```sh
mkdir -p ~/.config/tty-terminal
cp /usr/share/tty-terminal/config.example.toml ~/.config/tty-terminal/config.toml
```

example config:
```sh
# Restart TTY Terminal after changing these preferences.
# Rows and columns set the windowed size; fullscreen fills the monitor.
columns = 150
rows = 45
fullscreen = false
decorated = false # Show a title bar and window borders when true.

# Font height in logical pixels: any integer from 8 to 64, e.g. 20 or 24.
font_size = 16
scrollback_lines = 10000 # 0 disables history; maximum 1000000.
cursor_shape = "underline" # "underline", "block", or "ibeam"
cursor_blink = true
audible_bell = false

# Empty uses the launching process's directory. Supports ~ for your home.
directory = ""

```
