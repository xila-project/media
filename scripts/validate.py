"""Validate pinned brand assets, source provenance, productions and Python syntax."""
import ast
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
from brand import verify

ROOT=Path(__file__).resolve().parents[1]


def validate():
    lock=json.loads((ROOT/'assets/brand/lock.json').read_text())
    if lock['repository']!='xila-project/brand' or not re.fullmatch(r'[0-9a-f]{40}',lock['commit']):
        raise ValueError('Brand must be pinned to an official full commit')
    cache=ROOT/'assets/brand/upstream'
    manifest=json.loads((cache/'manifest.json').read_text())
    if manifest['version']!=lock['version']:
        raise ValueError('Brand version mismatch')
    for name,digest in lock['files'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError(f'Invalid brand path: {name}')
        verify((cache/name).read_bytes(),digest,name)
        if name in manifest['sha256'] and manifest['sha256'][name]!=digest:
            raise ValueError(f'Official manifest disagrees for {name}')
    for path in (ROOT/'productions').glob('*/production.json'):
        production=json.loads(path.read_text())
        if production['brandCommit']!=lock['commit']:
            raise ValueError(f'Production brand pin is stale: {path}')
    trailer=json.loads((ROOT/'productions/trailer/production.json').read_text())
    if sum(scene['duration'] for scene in trailer['scenes'])!=trailer['duration']:
        raise ValueError('Scene durations must sum to production duration')
    ids=set()
    assets=json.loads((ROOT/'assets/catalog.json').read_text())['assets']
    for asset in assets:
        for field in ['id','file','origin','license','author','sha256','kind']:
            if not asset.get(field):
                raise ValueError(f'Missing asset provenance field: {field}')
        if asset['id'] in ids:
            raise ValueError(f'Duplicate asset ID: {asset["id"]}')
        ids.add(asset['id'])
        path=(ROOT/asset['file']).resolve()
        if not path.is_relative_to(ROOT/'assets') or path.is_relative_to(cache):
            raise ValueError('Catalog entries must be source assets outside the brand cache')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=asset['sha256']:
            raise ValueError(f'Asset hash mismatch: {path}')
    by_id = {asset['id']: asset for asset in assets}
    for path in (ROOT/'productions').glob('*/production.json'):
        production = json.loads(path.read_text())
        for name, slot in production.get('screens', {}).items():
            dimensions = [slot['width'], slot['height']]
            position = slot['position']
            if any(not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0 for value in dimensions):
                raise ValueError(f'Invalid screen dimensions: {path}/{name}')
            if len(position) != 2 or any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in position):
                raise ValueError(f'Invalid screen position: {path}/{name}')
            if slot['asset'] is not None:
                asset = by_id.get(slot['asset'])
                if not asset or asset['kind'] != 'image' or any(not isinstance(asset.get(key), (int, float)) or not math.isfinite(asset[key]) or asset[key] <= 0 for key in ['width', 'height']):
                    raise ValueError(f'Screen requires a catalog image with dimensions: {path}/{name}')
    footage=trailer['footage']
    if footage:
        if trailer['footageStatus']!='recorded' or not any('/'+a['file']==footage and a['kind']=='footage' for a in assets):
            raise ValueError('Footage requires recorded status and a matching provenance entry')
    elif trailer['footageStatus']!='placeholder':
        raise ValueError('Missing footage must be explicitly marked as placeholder')
    for folder in ['scripts','tests','blender/scripts']:
        for path in (ROOT/folder).glob('*.py'):
            ast.parse(path.read_text(),filename=str(path))
    tracked=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
    for name in tracked:
        if name.startswith(('output/','node_modules/','assets/brand/upstream/')):
            raise ValueError(f'Generated artifact tracked: {name}')
    print(f'Validated brand {lock["version"]}, productions, {len(assets)} source assets and Python syntax')


if __name__=='__main__':
    validate()
