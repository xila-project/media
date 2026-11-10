"""Delete only known generated directories; source assets are never removed."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--brand',action='store_true',help='Also remove the downloaded brand cache')
args=parser.parse_args()
for target in [ROOT/'output', ROOT/'dist', *([ROOT/'assets/brand/upstream'] if args.brand else [])]:
    if target.is_symlink():
        raise ValueError(f'Refusing to follow symlink: {target}')
    if target.exists():
        shutil.rmtree(target)
        print(f'Removed {target.relative_to(ROOT)}')
