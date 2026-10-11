"""Inspect publishable files without printing potentially sensitive contents."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
result = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], capture_output=True)
if result.returncode:
    raise SystemExit('Initialize Git in this release directory before scanning.')
files = set(result.stdout.decode().split('\0')) - {''}
bad = []
private_parts = {'state', 'voices', 'models', 'reports', '__pycache__', '.venv', 'build', 'vendor'}
patterns = [
    re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(rb'\b(?:ghp_|github_pat_|hf_)[A-Za-z0-9_]{25,}'),
    re.compile(rb'[A-Za-z]:[\\/]Users[\\/][^\\/\s]+'),
    re.compile(rb'\b192\.168\.\d{1,3}\.\d{1,3}\b'),
]
for relative in sorted(files):
    path = ROOT / relative
    if not path.is_file():
        continue
    # Upstream examples may use these generic directory names; exclude only
    # application runtime paths, whose content is private by definition.
    parts = Path(relative).parts
    if private_parts.intersection(parts) or '.local.' in path.name or path.name.startswith('.env'):
        bad.append((relative, 'private runtime file'))
    data = path.read_bytes()
    if any(pattern.search(data) for pattern in patterns):
        bad.append((relative, 'credential or personal-path pattern'))
    if path.suffix.lower() in {'.wav', '.mp3', '.spk', '.rvq', '.gguf', '.safetensors', '.onnx', '.dll', '.exe'}:
        bad.append((relative, 'excluded media/model/binary'))
for name, reason in bad:
    print(f'{name}: {reason}')
print(f'Checked {len(files)} publishable files; findings: {len(bad)}')
raise SystemExit(bool(bad))
