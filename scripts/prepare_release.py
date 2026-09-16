#!/usr/bin/env python3
"""Build a deterministic source archive and AUR metadata from Git-tracked files.

Does not upload or create a tag. New files must be git-added first.
"""
import gzip
import hashlib
import io
import os
from pathlib import Path
import re
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    version = (ROOT / 'VERSION').read_text().strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise SystemExit('VERSION must contain a stable x.y.z version')
    prefix = f'tty-terminal-{version}'
    out = ROOT / 'dist' / version
    out.mkdir(parents=True, exist_ok=True)
    files = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    files = sorted(filter(None, files))
    if 'LICENSE' not in files or 'VERSION' not in files:
        raise SystemExit('Run git add on the intended source files first')
    epoch = int(os.environ.get('SOURCE_DATE_EPOCH', '0'))
    archive = out / f'{prefix}.tar.gz'
    with archive.open('wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=epoch) as zipped:
        with tarfile.open(fileobj=zipped, mode='w') as tar:
            for name in files:
                source = ROOT / name
                if not source.is_file() or source.is_symlink():
                    raise SystemExit(f'Unsupported release entry: {name}')
                data = source.read_bytes()
                info = tarfile.TarInfo(f'{prefix}/{name}')
                info.size = len(data)
                info.mtime = epoch
                info.mode = 0o755 if os.access(source, os.X_OK) else 0o644
                tar.addfile(info, io.BytesIO(data))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (out / 'SHA256SUMS').write_text(f'{digest}  {archive.name}\n')
    aur = out / 'aur'
    aur.mkdir(exist_ok=True)
    template = (ROOT / 'packaging/arch/PKGBUILD.in').read_text()
    (aur / 'PKGBUILD').write_text(template.replace('@VERSION@', version).replace('@SHA256@', digest))
    srcinfo = subprocess.check_output(['makepkg', '--printsrcinfo'], cwd=aur, text=True)
    (aur / '.SRCINFO').write_text(srcinfo)
    (aur / 'LICENSE').write_text((ROOT / 'LICENSE').read_text())
    print(f'Source: {archive}\nAUR metadata: {aur}\nSHA256: {digest}')


if __name__ == '__main__':
    main()
