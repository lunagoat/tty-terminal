#!/usr/bin/python
"""Experimental local CachyOS bundle, not a cross-distribution release builder.

See docs/DISTRIBUTION.md for baseline testing and corresponding-source requirements.
"""
from pathlib import Path
import shutil
import subprocess
import re
import sys

project = Path(__file__).resolve().parents[1]
dest = project / 'packaging/tty-terminal.AppDir'
if dest.exists():
    shutil.rmtree(dest)  # Generated build output only; rebuild without stale VTE files.
lib = dest / 'usr/lib'
app = dest / 'usr/share/tty-terminal'
app.mkdir(parents=True, exist_ok=True)
lib.mkdir(parents=True, exist_ok=True)

def copy(source, target):
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)

for name in ['tty_terminal.py', 'config.py', 'config.example.toml', 'README.md',
             'VERSION', 'LICENSE', 'THIRD_PARTY.md', 'build_font.py']:
    copy(project / name, app / name)
shutil.copytree(project / 'assets', app / 'assets', dirs_exist_ok=True)
version = f'python{sys.version_info.major}.{sys.version_info.minor}'
shutil.copytree(Path('/usr/lib') / version, lib / version, dirs_exist_ok=True,
                ignore=shutil.ignore_patterns('site-packages', '__pycache__', 'test', 'tests', 'idlelib', 'tkinter', 'ensurepip'))
copy(sys.executable, dest / 'usr/bin/python')
shutil.copytree('/usr/lib/kitty', lib / 'kitty', ignore=shutil.ignore_patterns('__pycache__'))
for binary in ['kitty', 'kitten']:
    copy('/usr/bin/' + binary, dest / 'usr/libexec' / binary)
    wrapper = dest / 'usr/bin' / binary
    wrapper.write_text('#!/bin/sh\nbase=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)\n'
                       'exec "$base/lib/ld-linux-x86-64.so.2" --library-path "$base/lib" '
                       f'"$base/libexec/{binary}" "$@"\n')
    wrapper.chmod(0o755)

queue = [dest / 'usr/bin/python', *lib.rglob('*.so'), * (dest / 'usr/libexec').iterdir()]
for name in ['libfontconfig.so.1', 'libEGL.so.1', 'libGL.so.1', 'libOpenGL.so.0',
             'libnss_files.so.2', 'libnss_dns.so.2']:
    source = Path('/usr/lib') / name
    if source.exists():
        copy(source, lib / name)
        queue.append(source)
seen = set()
while queue:
    source = queue.pop()
    if str(source) in seen:
        continue
    seen.add(str(source))
    output = subprocess.run(['ldd', str(source)], capture_output=True, text=True).stdout
    for filename in re.findall(r'(?:=>\s+|^\s*)(/[^\s]+)', output, re.M):
        dep = Path(filename)
        if dep.is_file() and not (lib / dep.name).exists():
            copy(dep, lib / dep.name)
            queue.append(dep)
copy('/usr/lib/ld-linux-x86-64.so.2', lib / 'ld-linux-x86-64.so.2')
shutil.copytree('/etc/fonts', dest / 'usr/etc/fonts', dirs_exist_ok=True, symlinks=False)
shutil.copytree('/usr/share/licenses', dest / 'usr/share/licenses', dirs_exist_ok=True,
                ignore_dangling_symlinks=True)
copy(project / 'packaging/AppRun', dest / 'AppRun')
copy(project / 'packaging/bootstrap.py', app / 'bootstrap.py')
copy(project / 'packaging/tty-terminal.svg', dest / 'tty-terminal.svg')
copy(project / 'packaging/tty-terminal.svg', dest / '.DirIcon')
(dest / 'tty-terminal.desktop').write_text('''[Desktop Entry]
Type=Application
Name=tty-terminal
Exec=tty-terminal
Icon=tty-terminal
Terminal=false
Categories=System;TerminalEmulator;
StartupWMClass=tty-terminal
''')
(dest / 'AppRun').chmod(0o755)
print(dest)
