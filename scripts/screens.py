"""Import a genuine screenshot and update one production slot, preserving its framing."""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from video import probe

ROOT = Path(__file__).resolve().parents[1]


def write_json(path, value):
    with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(value, handle, indent=2)
        handle.write('\n')
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def import_screen(root, production, slot, source, origin, author, license_name):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', production):
        raise ValueError('Invalid production name')
    if not all(value.strip() for value in [origin, author, license_name]):
        raise ValueError('Origin, author and license are required')
    suffix = source.suffix.lower()
    codecs = {'.png': 'png', '.jpg': 'mjpeg', '.jpeg': 'mjpeg'}
    if suffix not in codecs:
        raise ValueError('Screenshots must be PNG or JPEG')
    content = source.read_bytes()
    streams = probe(source)['streams']
    stream = next(item for item in streams if item.get('codec_type') == 'video')
    if stream.get('codec_name') != codecs[suffix]:
        raise ValueError('Screenshot encoding disagrees with its extension')
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(source), '-f', 'null', '-'], check=True)
    digest = hashlib.sha256(content).hexdigest()
    asset_id = f'screen-{digest}'
    relative = Path('assets/images/screens') / f'{asset_id}{suffix}'
    catalog_path = root / 'assets/catalog.json'
    # A separate lock remains stable while the JSON files are atomically replaced.
    with (root / 'assets/.screens.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        production_path = root / 'productions' / production / 'production.json'
        config = json.loads(production_path.read_text())
        selected = config['screens'][slot]
        catalog = json.loads(catalog_path.read_text())
        existing = next((asset for asset in catalog['assets'] if asset['id'] == asset_id), None)
        if existing:
            cached = root / existing['file']
            if hashlib.sha256(cached.read_bytes()).hexdigest() != digest:
                raise ValueError(f'Existing screenshot has been modified: {cached}')
        else:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            catalog['assets'].append({
                'id': asset_id, 'file': relative.as_posix(), 'kind': 'image',
                'origin': origin, 'author': author, 'license': license_name,
                'sha256': digest, 'width': stream['width'], 'height': stream['height'],
            })
            # If interrupted here, the previous slot still refers to a valid source.
            write_json(catalog_path, catalog)
        selected['asset'] = asset_id
        write_json(production_path, config)
    print(f'{production}/{slot} now uses {asset_id}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['import'])
    parser.add_argument('source', type=Path)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--production', required=True)
    parser.add_argument('--slot', required=True)
    parser.add_argument('--origin', required=True)
    parser.add_argument('--author', required=True)
    parser.add_argument('--license', required=True)
    args = parser.parse_args()
    import_screen(args.root.resolve(), args.production, args.slot, args.source,
                  args.origin, args.author, args.license)


if __name__ == '__main__':
    main()
