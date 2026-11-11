"""Render the launch film shot by shot, then assemble and validate the full cut.

Each shot renders independently in its set's time, is renumbered from zero,
assembled and validated before the film is concatenated. Use --shots to render
a subset and --keep to reuse shots whose validated MP4 already exists.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

from footage import retime
from video import concat, validate

ROOT = Path(__file__).resolve().parents[1]
BLENDER = ['blender', '--background', '--factory-startup', '--python-exit-code', '1']


def run(command):
    subprocess.run(command, check=True, cwd=ROOT)


def render_shot(config, shot, output, device):
    directory = output / 'shots' / shot['id']
    if (directory / 'frames').exists():
        shutil.rmtree(directory / 'frames')
    run(BLENDER + ['--python', str(ROOT / 'blender/scripts/launch_film.py'), '--',
                   '--shot', shot['id'], '--device', device])
    frames = sorted((directory / 'frames').glob('*.png'))
    expected = round(shot['duration'] * config['fps'])
    if len(frames) != expected:
        raise ValueError(f'{shot["id"]}: {len(frames)} frames, expected {expected}')
    # Shots render in set time; the assembly contract is a zero-based sequence.
    sequence = directory / 'sequence'
    if sequence.exists():
        shutil.rmtree(sequence)
    sequence.mkdir()
    for index, frame in enumerate(frames):
        frame.rename(sequence / f'{index:06d}.png')
    clip = directory.with_suffix('.mp4')
    run([sys.executable, 'scripts/video.py', 'assemble', str(sequence), str(clip),
         '--fps', str(config['fps']), '--preset', 'fast'])
    validate(clip, config['width'], config['height'], config['fps'], shot['duration'])
    return clip


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='auto')
    parser.add_argument('--shots', nargs='*', help='Shot IDs to (re)render; others must exist')
    parser.add_argument('--keep', action='store_true', help='Reuse existing validated shot clips')
    args = parser.parse_args()
    config = json.loads((ROOT / 'productions/launch-film/production.json').read_text())
    output = ROOT / 'output/launch-film' / f'review-{config["review"]}'
    run([sys.executable, 'scripts/brand.py'])
    run(['node', 'scripts/prepare-copy.mjs', 'launch-film'])
    # Genuine recordings, retimed by holding real frames (speed is disclosed in the README).
    for key, spec in config['footage'].items():
        retime(spec['asset'], ROOT / 'output/launch-film/footage' / key, spec['duration'],
               config['fps'], spec['speed'], spec['start'])
    clips = []
    for shot in config['shots']:
        clip = output / 'shots' / f'{shot["id"]}.mp4'
        selected = args.shots is None or shot['id'] in args.shots
        if selected and not (args.keep and clip.exists()):
            render_shot(config, shot, output, args.device)
        validate(clip, config['width'], config['height'], config['fps'], shot['duration'])
        clips.append(clip)
    identity = config['identity']
    ending = ROOT / 'output' / identity['production'] / f'{identity["production"]}.mp4'
    if args.shots is None or 'identity' in args.shots or not ending.exists():
        run(['npm', 'run', 'render', '--', '--production', identity['production'],
             '--resolution', f'{config["width"]}x{config["height"]}', '--preset', 'fast'])
    validate(ending, config['width'], config['height'], config['fps'], identity['duration'])
    clips.append(ending)
    film = output / 'launch-film.mp4'
    concat(clips, film)
    validate(film, config['width'], config['height'], config['fps'], config['duration'])


if __name__ == '__main__':
    main()
