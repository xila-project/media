"""Validate pinned brand assets, source provenance, productions and Python syntax."""
import ast
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
from brand import verify
from lyric_align import LOW_CONFIDENCE, METER, MIN_CONFIDENCE, alignment_report, position

ROOT=Path(__file__).resolve().parents[1]


def validate_grid_sections(cues, path):
    next_bar = 1
    for section in cues['sections']:
        if section['startBar'] != next_bar or type(section['bars']) is not int or section['bars'] <= 0:
            raise ValueError(f'Invalid cue section span: {path}/{section["id"]}')
        next_bar += section['bars']
    if next_bar != cues['bars'] + 1:
        raise ValueError(f'Cue sections must span the score: {path}')


def validate_measured_cues(cues, path):
    bpm, duration = cues['bpm'], cues['duration']
    if cues['beatsPerBar'] != METER:
        raise ValueError(f'Invalid measured cue meter: {path}')

    def check_span(cue, lower, upper, label):
        start, end = cue['start'], cue['end']
        if not lower <= start <= end <= upper:
            raise ValueError(f'Invalid measured cue time: {path}/{label}')
        if (cue['at'], cue['endAt']) != (position(start, bpm), position(end, bpm)):
            raise ValueError(f'Measured cue grid stamps disagree: {path}/{label}')

    def check_missing(cue):
        if not cue.get('missing') or {'start', 'end', 'at', 'endAt', 'startBar', 'bars'} & cue.keys():
            raise ValueError(f'Missing cue has a timing or lacks its flag: {path}/{cue["id"]}')

    by_section = {section['id']: [] for section in cues['sections']}
    previous_start = 0
    for line in cues['lines']:
        group = by_section[line['sectionId']]
        label = line['id']
        words = line['words']
        if line.get('missing'):
            check_missing(line)
            if words or line.get('low_confidence'):
                raise ValueError(f'Missing lyric has word cues or low confidence: {path}/{label}')
            continue
        check_span(line, previous_start, duration, label)
        previous_start = line['start']
        confidence = line['confidence']
        if (not MIN_CONFIDENCE <= confidence <= 1
                or line.get('low_confidence', False) != (confidence < LOW_CONFIDENCE)):
            raise ValueError(f'Invalid measured cue confidence: {path}/{label}')
        if not words or (words[0]['start'], words[-1]['end']) != (line['start'], line['end']):
            raise ValueError(f'Line bounds disagree with its words: {path}/{label}')
        word_start = line['start']
        for word in words:
            check_span(word, word_start, line['end'], f'{label}/{word["text"]}')
            word_start = word['start']
        group.append(line)

    bars_per_second = bpm / (METER * 60)
    for section in cues['sections']:
        label = section['id']
        lines = by_section[label]
        if not lines:
            check_missing(section)
            continue
        check_span(section, 0, duration, label)
        start, end = section['start'], section['end']
        if (section.get('missing')
                or (start, end) != (lines[0]['start'], lines[-1]['end'])
                or not math.isclose(section['startBar'], 1 + start * bars_per_second)
                or not math.isclose(section['bars'], (end - start) * bars_per_second)):
            raise ValueError(f'Section bounds disagree with its lyric lines: {path}/{label}')

    report = path.with_name('alignment-report.txt')
    if report.exists() and report.read_text(encoding='utf-8') != alignment_report(cues):
        raise ValueError(f'Alignment report disagrees with measured cues: {report}')


def validate_cues(path):
    cues = json.loads(path.read_text())
    measured = cues.get('timing') == 'measured'
    bpm, meter, bars = (cues[key] for key in ('bpm', 'beatsPerBar', 'bars'))
    if not all(type(value) is int and value > 0 for value in (bpm, meter)):
        raise ValueError(f'Invalid cue tempo or meter: {path}')
    if (type(bars) not in (int, float) or not math.isfinite(bars) or bars <= 0
            or (not measured and type(bars) is not int)):
        raise ValueError(f'Invalid cue bar count: {path}')
    if cues['duration'] <= 0 or not math.isclose(cues['duration'], bars * meter * 60 / bpm, rel_tol=0, abs_tol=0.001):
        raise ValueError(f'Cue duration disagrees with score grid: {path}')
    for key in ('sections', 'lines', 'events'):
        ids = [item['id'] for item in cues[key]]
        if len(set(ids)) != len(ids):
            raise ValueError(f'Duplicate cue IDs in {key}: {path}')
    if measured:
        validate_measured_cues(cues, path)
    else:
        validate_grid_sections(cues, path)


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
    for path in (ROOT/'productions').rglob('cues.json'):
        validate_cues(path)
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
