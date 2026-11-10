"""Resolve exact upstream assets; the ignored cache is never an editable source."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def verify(data, expected, name):
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f"Brand hash mismatch: {name}")


def sync(local=None, destination=None):
    lock = json.loads((ROOT / "assets/brand/lock.json").read_text())
    destination = destination or ROOT / "assets/brand/upstream"
    if local:
        result = subprocess.run(["git", "-C", str(local), "rev-parse", "HEAD"], capture_output=True, text=True)
        if result.returncode or result.stdout.strip() != lock["commit"]:
            raise ValueError("Local brand checkout must be at the locked commit")
    for name, expected in lock["files"].items():
        target = destination / name
        if target.exists():
            verify(target.read_bytes(), expected, name)
            continue
        if local:
            data = (local / name).read_bytes()
        else:
            url = f'https://raw.githubusercontent.com/{lock["repository"]}/{lock["commit"]}/{name}'
            with urllib.request.urlopen(url, timeout=60) as response:
                data = response.read()
        verify(data, expected, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(f'Brand {lock["version"]} verified at {lock["commit"]}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", type=Path)
    args = parser.parse_args()
    sync(args.local)
