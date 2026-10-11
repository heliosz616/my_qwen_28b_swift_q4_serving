"""Package only Git-visible source files, never the local runtime or Git history."""
from pathlib import Path
import subprocess
import sys
import zipfile

root = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(root / 'tools/check_release.py')], check=True)
files = subprocess.check_output(['git', '-C', str(root), 'ls-files', '--cached', '--others', '--exclude-standard', '-z']).decode().split('\0')
destination = root.parent / (root.name + '-source.zip')
with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
    for relative in sorted(set(files) - {''}):
        path = root / relative
        if path.is_file():
            archive.write(path, relative)
print(f'Created {destination.name}')
