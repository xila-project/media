"""Render the cinematic product passage and validate its assembled review."""
import argparse
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
from video import validate

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--production', choices=['product-reveal', 'architecture-reveal'], default='product-reveal')
    parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='auto')
    args = parser.parse_args()
    config = json.loads((ROOT / 'productions' / args.production / 'production.json').read_text())
    if not re.fullmatch(r'[0-9]{3}', config['review']):
        raise ValueError('Review must be a three-digit version')
    output = ROOT / 'output' / args.production / f'review-{config["review"]}'
    # Complete sequences are regenerated; other numbered review cuts remain available.
    if (output / 'frames').exists():
        shutil.rmtree(output / 'frames')
    subprocess.run(['blender', '--background', '--factory-startup', '--python-exit-code', '1',
                    '--python', str(ROOT / 'blender/scripts' / (args.production.replace('-', '_') + '.py')), '--',
                    '--device', args.device], check=True, cwd=ROOT)
    count = len(list((output / 'frames').glob('*.png')))
    if count != config['fps'] * config['duration']:
        raise ValueError(f'Incomplete product sequence: {count} frames')
    video = output / f'{args.production}.mp4'
    subprocess.run([sys.executable, str(ROOT / 'scripts/video.py'), 'assemble', str(output / 'frames'),
                    str(video), '--fps', str(config['fps']), '--preset', 'fast'], check=True, cwd=ROOT)
    validate(video, config['width'], config['height'], config['fps'], config['duration'])


if __name__ == '__main__':
    main()
