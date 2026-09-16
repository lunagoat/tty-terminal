#!/usr/bin/python
"""Exercise the installed launcher or an AppImage with real Kitty image traffic."""
import base64
import json
import os
from pathlib import Path
import select
import struct
import subprocess
import sys
import tempfile
import termios
import time
import tty
import zlib

ROOT = Path(__file__).resolve().parent


def child(output):
    fd = sys.stdin.fileno()
    previous = termios.tcgetattr(fd)
    tty.setraw(fd)
    response = b''
    try:
        os.write(1, b'\x1b_Ga=q,i=71,s=1,v=1,f=24;////\x1b\\')
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and b'\x1b\\' not in response:
            if select.select([fd], [], [], 0.2)[0]:
                response += os.read(fd, 4096)
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, previous)
    assert b'i=71;OK' in response, repr(response)
    columns, rows = os.get_terminal_size()
    assert (columns, rows) == (100, 30), (columns, rows)
    print('\033[2J\033[HMW@0 iIl .,:; VGA font')
    print('\033[1mMW@0 iIl .,:; VGA font\033[0m')
    print('tty-terminal | native Kitty images | VGA console font')
    print('ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789')
    print('')
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    width, height = 240, 96
    rows_data = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            row.extend(((255, 85, 85), (85, 255, 85), (85, 85, 255), (255, 255, 85))[x // 60])
        rows_data.append(row)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(b''.join(rows_data))) + chunk(b'IEND', b'')
    sys.stdout.flush()
    kitten = Path(os.environ['KITTY_INSTALLATION_DIR']).parents[1] / 'bin/kitten'
    subprocess.run([str(kitten), 'icat', '--stdin=yes', '--transfer-mode=stream'], input=png, check=True)
    print('Inline image rendered above. Normal shell input remains available.', flush=True)
    result = dict(image_query=response.decode(), columns=columns, rows=rows,
                  term=os.environ.get('TERM'), name='pending',
                  bundled_paths={k: os.environ.get(k) for k in ('PYTHONHOME', 'GI_TYPELIB_PATH', 'FONTCONFIG_FILE')})
    Path(output).write_text(json.dumps(result, indent=2))
    time.sleep(6)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--child':
        child(sys.argv[2])
        return
    launcher = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / 'tty_terminal.py')
    with tempfile.TemporaryDirectory(prefix='tty-kitty-test-') as folder:
        result = Path(folder) / 'result.json'
        command = [launcher, '--config', str(Path(folder) / 'absent.toml'), '--windowed',
                   '--columns', '100', '--rows', '30', '--font-size', '16',
                   '-e', '/bin/bash', '--noprofile', '--norc', '-c',
                   '/usr/bin/python "$1" --child "$2" && fastfetch --structure Terminal --format json > "$3"; exit_code=$?; exit "$exit_code"',
                   'test', str(Path(__file__).resolve()), str(result), str(result) + '.fetch']
        proc = subprocess.Popen(command)
        try:
            deadline = time.monotonic() + 15
            while not result.exists() and proc.poll() is None and time.monotonic() < deadline:
                time.sleep(0.2)
            assert result.exists(), 'Terminal did not complete the image test'
            data = json.loads(result.read_text())
            print(json.dumps(data, indent=2), flush=True)
            assert not any(data['bundled_paths'].values()), data
            if launcher.endswith('test_visual.py'):
                subprocess.run(['import', '-window', 'tty-terminal', str(ROOT / 'preview-kitty.png')], timeout=8, check=True)
            assert proc.wait(timeout=12) == 0
            name = json.loads(Path(str(result) + '.fetch').read_text())[0]['result']['prettyName']
            assert name == 'tty-terminal', name
        finally:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=5)
    print('PASS: Kitty image query, icat PNG, dimensions, Fastfetch name, clean child environment')


if __name__ == '__main__':
    main()
