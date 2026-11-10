"""Verify release file hashes without modifying retained evidence."""
import hashlib
import json
from pathlib import Path
root = Path(__file__).resolve().parent
checksums = json.loads((root / 'checksums.json').read_text())
for name, expected in checksums.items():
    actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit('FAIL: ' + name)
print('PASS: %d release files match SHA-256 checksums.' % len(checksums))
