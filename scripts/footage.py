"""Import native screen recordings as source footage and retime them honestly.

import: copy a recorded PNG sequence and its frames.json timestamps into
assets/footage/<name>/, write a manifest with per-frame hashes and register it
in assets/catalog.json.
retime: write a zero-based sequence at a delivery frame rate by holding the
latest real frame at each output time. No frames are interpolated or invented;
speed > 1 is an accelerated presentation and must be disclosed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'assets/catalog.json'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def png_size(path):
    with open(path, 'rb') as handle:
        header = handle.read(24)
    if header[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'Not a PNG: {path}')
    return struct.unpack('>II', header[16:24])


def import_recording(source, name, origin, author, license_id):
    source = Path(source)
    timing = json.loads((source / 'frames.json').read_text())
    target = ROOT / 'assets/footage' / name
    if target.exists():
        raise FileExistsError(f'Footage already imported: {target}')
    target.mkdir(parents=True)
    frames = []
    size = None
    for entry in timing['frames']:
        frame = source / entry['file']
        current = png_size(frame)
        if size and current != size:
            raise ValueError(f'Inconsistent frame size: {frame}')
        size = current
        shutil.copy2(frame, target / entry['file'])
        frames.append({'file': entry['file'], 'sha256': sha256(frame), 'time': entry['timestampSeconds']})
    shutil.copy2(source / 'frames.json', target / 'frames.json')
    manifest = {'name': name, 'width': size[0], 'height': size[1], 'frameCount': len(frames),
                'durationSeconds': timing['durationSeconds'], 'timestampMeaning': timing['timestampMeaning'],
                'frames': frames}
    path = target / 'manifest.json'
    path.write_text(json.dumps(manifest, indent=2) + '\n')
    catalog = json.loads(CATALOG.read_text())
    catalog['assets'].append({'id': f'footage-{name}', 'file': str(path.relative_to(ROOT)), 'kind': 'footage',
                              'origin': origin, 'author': author, 'license': license_id,
                              'sha256': sha256(path), 'width': size[0], 'height': size[1]})
    CATALOG.write_text(json.dumps(catalog, indent=2) + '\n')
    print(f'Imported {len(frames)} frames as footage-{name}')


def load(asset_id):
    asset = next(a for a in json.loads(CATALOG.read_text())['assets'] if a['id'] == asset_id)
    path = ROOT / asset['file']
    if sha256(path) != asset['sha256']:
        raise ValueError(f'Manifest hash mismatch: {asset_id}')
    manifest = json.loads(path.read_text())
    for frame in manifest['frames']:
        if sha256(path.parent / frame['file']) != frame['sha256']:
            raise ValueError(f'Frame hash mismatch: {frame["file"]}')
    return path.parent, manifest


def retime(asset_id, output, duration, fps=30, speed=1.0, start=0.0):
    directory, manifest = load(asset_id)
    frames = manifest['frames']
    origin = frames[0]['time']
    output = Path(output)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    used = []
    for index in range(round(duration * fps)):
        moment = origin + start + index / fps * speed
        chosen = max((f for f in frames if f['time'] <= moment), key=lambda f: f['time'], default=frames[0])
        target = output / f'{index:06d}.png'
        try:
            os.link(directory / chosen['file'], target)
        except OSError:
            shutil.copy2(directory / chosen['file'], target)
        used.append(chosen['file'])
    if moment > frames[-1]['time'] + .5:
        raise ValueError(f'{asset_id}: retime runs past the recording ({moment - origin:.2f}s)')
    (output / 'retime.json').write_text(json.dumps({'asset': asset_id, 'speed': speed, 'start': start,
                                                    'fps': fps, 'sourceFrames': used}, indent=2) + '\n')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    importer = commands.add_parser('import')
    importer.add_argument('source', type=Path)
    importer.add_argument('name')
    importer.add_argument('--origin', required=True)
    importer.add_argument('--author', required=True)
    importer.add_argument('--license', required=True)
    timing = commands.add_parser('retime')
    timing.add_argument('asset')
    timing.add_argument('output', type=Path)
    timing.add_argument('--duration', type=float, required=True)
    timing.add_argument('--fps', type=int, default=30)
    timing.add_argument('--speed', type=float, default=1.0)
    timing.add_argument('--start', type=float, default=0.0)
    args = parser.parse_args()
    if args.command == 'import':
        import_recording(args.source, args.name, args.origin, args.author, args.license)
    else:
        retime(args.asset, args.output, args.duration, args.fps, args.speed, args.start)


if __name__ == '__main__':
    main()
