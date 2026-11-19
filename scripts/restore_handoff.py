#!/usr/bin/env python3
"""Reassemble and safely unpack the exact Gordia reference handoff archive."""
from pathlib import Path
import hashlib
import io
import sys
import zipfile

ROOT = Path(__file__).resolve().parent.parent
PARTS = ROOT / "handoff_parts"
EXPECTED_PARTS = 27
EXPECTED_BYTES = 20889584
EXPECTED_SHA256 = "07ae448d1616d5123db6554d1f779e89d798d34f354ac1c5f29623660b9af071"

def restore():
    items = [PARTS / f"part_{n:02d}.bin" for n in range(EXPECTED_PARTS)]
    missing = [str(p.relative_to(ROOT)) for p in items if not p.is_file()]
    if missing:
        raise RuntimeError("Missing handoff pieces: " + ", ".join(missing))
    raw = b"".join(p.read_bytes() for p in items)
    if len(raw) != EXPECTED_BYTES:
        raise RuntimeError(f"Wrong archive length: {len(raw)} != {EXPECTED_BYTES}")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        raise RuntimeError(f"SHA256 mismatch: {digest}")
    count = 0
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            candidate = (ROOT / info.filename).resolve()
            if not candidate.is_relative_to(ROOT):
                raise RuntimeError(f"Unsafe ZIP entry: {info.filename}")
            if not candidate.exists():
                candidate.parent.mkdir(parents=True, exist_ok=True)
                candidate.write_bytes(z.read(info))
                print(f"Restored {info.filename}")
            else:
                print(f"Already present: {info.filename}")
            count += 1
    if count != 15:
        raise RuntimeError(f"Expected 15 source files, got {count}")
    print(f"Verified archive SHA256 {digest}; {count} file entries present.")

if __name__ == "__main__":
    try:
        restore()
    except Exception as exc:
        print("Archive restoration failed:", exc, file=sys.stderr)
        raise SystemExit(1)
