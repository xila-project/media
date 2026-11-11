"""Launch film shots. Each shot builds one set of the shared world in set time.

Usage: blender --background --factory-startup --python blender/scripts/launch_film.py --
       --shot 04-execution [--still 120] [--samples 8] [--device cuda]
Routes, pauses and object counts are artwork; the mark, captures and stroke
geometry come from official and measured sources.
"""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from film_world import ROOT, World, ripple, smooth_animation  # noqa: E402

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--shot', required=True)
parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='auto')
parser.add_argument('--still', type=int, action='append', help='Set-time frame numbers')
parser.add_argument('--samples', type=int)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
config = json.loads((ROOT / 'productions/launch-film/production.json').read_text())
shot = next(s for s in config['shots'] if s['id'] == args.shot)
look = config['look']
W = World(config, look, shot['offset'] + shot['duration'], args.device, args.samples or config['samples'])
W.copy_dir = ROOT / 'output/launch-film/copy'
W.scene.frame_start = W.frame(shot['offset'])
W.scene.frame_end = W.frame(shot['offset']) + W.frame(shot['duration']) - 1
ROUTE = .38  # measured 30 px stroke at 12.6 mm/px


def facing(center, toward):
    """Yaw so an upright copy plane faces a point."""
    d = Vector(toward[:2]) - Vector(center[:2])
    return math.atan2(d.x, -d.y)


def stepped(start, moves):
    points = [tuple(start)]
    for dx, dy in moves:
        x, y = points[-1]
        points.append((x + dx, y + dy))
    return points


def fade(on, off=None, ramp=.6):
    keys = [(0, 0), (on, 0), (on + ramp, 1)]
    if off is not None:
        keys += [(off, 1), (off + ramp, 0)]
    return keys


def rise(obj, height, start, duration=.8, below=None):
    """Move an object up from below the floor into place."""
    final = obj.location.z
    W.key(obj, 'location', [(0, (obj.location.x, obj.location.y, final - (below or height))),
                            (start, (obj.location.x, obj.location.y, final - (below or height))),
                            (start + duration, (obj.location.x, obj.location.y, final))])
    smooth_animation(obj)


def strength_material(name, keys, value=1.0):
    mat, shader = W.emission(name, value, 0)
    W.key_socket(shader.inputs['Strength'], keys, mat.node_tree)
    return mat


# --- Sets ------------------------------------------------------------------
def recognition():
    """Extruded mark in satin metal under a moving strip; it ignites white, then ripples."""
    W.floor()
    W.haze(.002)
    width = 2.0
    curves_mat = []
    arms = W.mark((0, 0), width, z=.04, extrude=.06, mat=W.shared('clear-space'))
    for index, obj in enumerate(arms):
        mat = bpy.data.materials.new(f'Mark module {index}')
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        metal = nodes['Principled BSDF']
        metal.inputs['Base Color'].default_value = (.12, .12, .12, 1)
        metal.inputs['Metallic'].default_value = .85
        metal.inputs['Roughness'].default_value = .24
        glow = nodes.new('ShaderNodeEmission')
        glow.inputs['Strength'].default_value = look['markStrength']
        mix = nodes.new('ShaderNodeMixShader')
        links.new(metal.outputs[0], mix.inputs[1])
        links.new(glow.outputs[0], mix.inputs[2])
        links.new(mix.outputs[0], nodes['Material Output'].inputs['Surface'])
        W.key_socket(mix.inputs[0], [(0, 0), (4.6, 0), (5.2, 1)], mat.node_tree)
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        curves_mat.append((obj, glow, mat))
    # SVG import order (center, BR, TR, TL, BL) -> Core order TL, BL, BR, TR.
    for entry in ripple(shot['offset'] + shot['duration'], config['fps'], 5.3):
        for index, source in enumerate([3, 4, 1, 2]):
            obj, glow, mat = curves_mat[source]
            state = entry['arms'][index]
            origin = obj.get('origin') or list(obj.location)
            obj['origin'] = origin
            obj.location = Vector(origin) + Vector((state['x'] * width / 320, -state['y'] * width / 320, 0))
            obj.keyframe_insert('location', frame=entry['frame'])
            glow.inputs['Strength'].default_value = look['markStrength'] * state['opacity'] / 255
            glow.inputs['Strength'].keyframe_insert('default_value', frame=entry['frame'])
    strip = W.area('Moving strip', (-2.5, .8, 2), (0, 0, 0), 450, 3.5, .18)
    for t, position, power in [(0, (-2.5, .8, 2), .5), (2, (-1.4, 1.1, 2.4), 250), (4.2, (.4, .8, 2.8), 450), (6, (1.2, .9, 3.2), 300)]:
        W.aim(strip, position, (0, 0, 0))
        strip.data.energy = power
        for data, prop in [(strip, 'location'), (strip, 'rotation_euler'), (strip.data, 'energy')]:
            data.keyframe_insert(prop, frame=W.frame(t))
    W.area('Edge strip', (1.8, -1.5, 1.6), (0, 0, 0), 120, 3, .1)


def foundation_routes():
    return [stepped((-.5, 1.63), [(0, 4.4), (-3.5, 0), (0, 8), (2.5, 0), (0, 46)]),
            stepped((0, 1.63), [(0, 7.4), (1.5, 0), (0, 9), (-1.5, 0), (0, 42)]),
            stepped((.5, 1.63), [(0, 4.4), (3.5, 0), (0, 8), (-2.5, 0), (0, 46)])]


def foundation(dark_after=None):
    """Floor slabs arrive into alignment around the mark; three routes leave it."""
    W.floor()
    W.haze()
    W.lights()
    W.mark((0, 0), 2.0)
    tile = 4
    for i in range(-4, 5):
        for j in range(-3, 7):
            if i == 0 and j == 0:
                continue
            ring = max(abs(i), abs(j))
            slab = W.box(f'Slab {i},{j}', (i * tile, j * tile, -.2 + .003), (tile - .03, tile - .03, .4), W.floor_material)
            rise(slab, 0, .5 + .16 * ring, 1.0, below=-(.5 + .3 * ring))
    for index, points in enumerate(foundation_routes()):
        keys, _ = W.metered(points, 4.4 + .5 * index, 9, .15)
        W.route(f'Foundation route {index}', points, ROUTE, keys)


def field():
    """A dense ordered field locking in rows around a central route and foundation."""
    W.floor()
    W.haze()
    W.lights([["Backlight", [4, 50, 9], [0, 20, 1], 2600, 10], ["Low rim", [-14, -2, 1.2], [0, 6, .8], 300, 3]])
    route = [(0, -40), (0, 22)]
    W.route('Central route', route, ROUTE, [(0, 0, .3), (6, 0, 1)])
    W.route('Exit pulse', [(0, 30), (0, 80)], ROUTE, [(0, 0, 0), (7.2, 0, 0), (8.2, 0, .25), (10, .3, .7)], inlay=False)
    W.box('Central foundation', (0, 26, .4), (10, 8, .8), W.shared('block'))
    W.box('Foreground edge', (-1.1, -3, 1.6), (.8, .8, 3.2), W.shared('block'))
    for row, y in enumerate(range(-8, 22, 2)):
        for side in (-1, 1):
            for m in range(6):
                seed = (row * 7 + m * 13 + (side + 1) * 5) % 11 / 10
                height = .5 + 2.6 * seed
                x = side * (2.4 + 1.6 * m)
                block = W.box(f'Field {row},{side},{m}', (x, y, height / 2), (1.1, 1.1, height), W.shared('block'))
                rise(block, height, .2 + row * .14 + m * .03, .6)
    W.copy('os', (0, 7, 1.9), .3, keys=fade(1.0, 8.6))
    W.copy('rust', (5.6, 21, 1.25), .2, yaw=facing((5.6, 21), (1, 9)), keys=fade(3.0))


def execution(mode='reveal'):
    """Light leaves the mark along the measured Pixel Painter strokes into the surface."""
    W.floor()
    W.haze()
    W.lights()
    source = json.loads((ROOT / config['strokesFrom']).read_text())
    unit, origin = source['floor']['metresPerPixel'], source['floor']['originPixel']
    mono = source['monolith']
    W.mark(tuple(source['mark']['center']), source['mark']['width'])
    arrival = 0
    for index, pixels in enumerate(source['strokes']['paths']):
        points = [((x - origin[0]) * unit, -(y - origin[1]) * unit) for x, y in pixels]
        points += [(mono['entryX'][index], points[-1][1]), (mono['entryX'][index], mono['frontY'])]
        keys, end = W.metered(points, .5 + .14 * index, 4.5, .16)
        arrival = max(arrival, end)
        if mode == 'power':
            keys = [(0, 0, 1), (3 + .2 * index, 0, 1), (6 + .2 * index, 0, 0)]
        W.route(f'Stroke {index + 1}', points, source['strokes']['width'] * unit, keys)
    if mode == 'power':
        pulse = [((x - origin[0]) * unit, -(y - origin[1]) * unit) for x, y in source['strokes']['paths'][1]]
        W.route('Final pulse', pulse, source['strokes']['width'] * unit * .5,
                [(0, 0, 0), (6.2, 0, 0), (6.6, 0, .08), (8.2, .92, 1), (8.5, 1, 1)], inlay=False)
    painter, drawer = config['captures']['painter'], config['captures']['drawer']
    screen = W.screen_material('Genuine capture', painter,
                               [(0, 0), (6.8, 0), (7.4, 1)] if mode == 'reveal' else [(0, 1), (2, 1), (2.6, 0)])
    if mode == 'reveal':
        # The first real drawer frame takes over as the camera reaches the surface.
        nodes, links = screen.node_tree.nodes, screen.node_tree.links
        from film_world import catalog_file
        second = nodes.new('ShaderNodeTexImage')
        second.image = bpy.data.images.load(str(catalog_file(drawer)[0]))
        mix = nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        links.new(W.screen_image.outputs['Color'], mix.inputs['A'])
        links.new(second.outputs['Color'], mix.inputs['B'])
        links.new(mix.outputs['Result'], nodes['Principled BSDF'].inputs['Emission Color'])
        W.key_socket(mix.inputs['Factor'], [(0, 0), (11.1, 0), (11.3, 1)], screen.node_tree)
    W.monolith('Result surface', mono['centerX'], mono['frontY'], mono['width'], 1.6, screen=screen)
    for name, x, y, width, aspect, at in [('Second surface', -2.6, 5.6, 3.2, 1.0, 5.0), ('Third surface', 11.6, 4.4, 3.2, 2.0, 5.5)]:
        keys = [(0, 0), (at + .8, 0), (at + 1.4, .07)]
        if mode == 'power':
            keys = [(0, .07), (2.4, .07), (3.0, 0)]
        pivot, _ = W.monolith(name, x, y, width, aspect, screen=W.screen_material(f'{name} glow', None, keys))
        if mode == 'reveal':
            rise(pivot, width / aspect + .5, at, 1.0)
    label = W.copy('app', (8.6, 3.0, .004), .09, upright=False, keys=[(0, .5)])
    if mode == 'reveal':
        camera = (-9, -15)
        W.copy('upon', (-1.0, 8.0, 4.5), .42, yaw=facing((-1.0, 8.0), camera), keys=fade(4.4, 7.4))
        W.copy('wasm', (-1.0, 8.0, 3.85), .17, yaw=facing((-1.0, 8.0), camera), keys=fade(4.8, 7.4))
    return label


def proof():
    """Genuine native recordings fill the surface; the stroke continues as a route."""
    W.floor()
    W.haze()
    W.lights([["Backlight", [4, 20, 8], [0, 0, 1.5], 1200, 6]])
    screen = W.screen_material('Genuine recording', None, [(0, 1)])
    nodes, links = screen.node_tree.nodes, screen.node_tree.links
    result = None
    # Each entry: (footage key, set time it starts). Later entries take over at their start.
    for key, at in shot['footage']:
        node = nodes.new('ShaderNodeTexImage')
        image, count, first = W.sequence_image(ROOT / 'output/launch-film/footage' / key, W.frame(at))
        W.bind_sequence(node, image, count, first)
        if result is None:
            result = node.outputs['Color']
            continue
        mix = nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        links.new(result, mix.inputs['A'])
        links.new(node.outputs['Color'], mix.inputs['B'])
        W.key_socket(mix.inputs['Factor'], [(0, 0), (at - 1 / W.fps, 0), (at, 1)], screen.node_tree)
        for curve in screen.node_tree.animation_data.action.fcurves:
            for point in curve.keyframe_points:
                point.interpolation = 'CONSTANT'
        result = mix.outputs['Result']
    links.new(result, nodes['Principled BSDF'].inputs['Emission Color'])
    W.monolith('Capture surface', 0, 0, 6, 1.6, screen=screen)
    route = stepped((3.2, -.1), [(8, 0), (0, 2), (6, 0), (0, -2), (30, 0)])
    W.route('Stroke continues', route, ROUTE, [(0, 0, 0), (5.8, 0, 0), (9, 0, .45)])


def embedded():
    """A compact board made monumental by a macro camera; surfaces open around it."""
    W.floor()
    W.haze(.003)
    W.lights([["Backlight", [2, 9, 4], [0, 0, .2], 900, 4], ["Low rim", [-6, -1, .5], [0, 0, .2], 120, 2]])
    W.box('Compact foundation', (0, 0, .08), (4, 2.6, .16), W.shared('frame'))
    for index in range(7):
        y = -1.0 + index * .33
        points = [(-1.9, y, 0), (-.6 + .2 * index, y, 0), (-.6 + .2 * index, y + .15, 0), (1.9, y + .15, 0)]
        keys, _ = W.metered(points, .5 + .25 * index, 1.4, .12, .15)
        light = W.route(f'Board route {index}', points, .045, keys, strength=4)
        light.location.z += .16
        bpy.data.objects[f'Board route {index} inlay'].location.z += .16
    for index, (x, y) in enumerate([(-1.2, .7), (-.3, -.6), (.6, .5), (1.3, -.4), (.1, .1), (-1.4, -.7)]):
        W.box(f'Module {index}', (x, y, .2), (.34, .34, .08), W.shared('block'))
    W.copy('embedded', (0, 2.4, .5), .09, keys=fade(3.0, 7.4))
    for index, (x, y, width, aspect) in enumerate([(-4.5, 3.6, 1.6, 1.0), (4.8, 3.2, 2.4, 1.78), (-2.2, 5.6, 1.2, .75), (2.6, 6.4, 2.8, 2.4)]):
        at = 8.0 + .3 * index
        pivot, _ = W.monolith(f'Output surface {index}', x, y, width, aspect, base=.12, depth=.15,
                              screen=W.screen_material(f'Output {index}', None, [(0, 0), (at + .6, 0), (at + 1.2, .08)]))
        rise(pivot, width / aspect + .3, at, 1.0)


def namespace():
    """One request, a junction and three resource forms that respond differently."""
    W.floor()
    W.haze()
    W.lights([["Backlight", [6, 18, 8], [6, 0, .5], 1600, 6], ["Low rim", [-14, -2, 1.2], [0, 0, .6], 250, 3]])
    W.box('Junction', (0, 0, .18), (.7, .7, .36), W.shared('frame'))
    request = [(-18, 0), (-.4, 0)]
    W.route('Request', request, ROUTE, [(0, 0, 0), (.2, 0, 0), (1.8, 0, 1)])
    branches = {
        'files': (stepped((.4, .15), [(1.6, 0), (0, 4), (3.6, 0), (0, 1.6)]), 1.9, 9.6),
        'devices': (stepped((.4, 0), [(7.6, 0)]), 7.2, 7.2),
        'pipes': (stepped((.4, -.15), [(1.6, 0), (0, -3.85), (2.6, 0)]), 8.4, 8.4),
    }
    for name, (points, first, second) in branches.items():
        W.route(f'Branch {name}', points, ROUTE * .8, [(0, 0, 0), (first, 0, 0), (first + .6, 0, 1)])
    # Files: a stack of plates lights from the bottom up.
    for index in range(7):
        keys = [(0, 0), (2.5 + .06 * index, 0), (2.7 + .06 * index, 2.4), (3.6, .25),
                (11.0, .25), (11.2, 3), (12, 1.2)]
        W.box(f'File plate {index}', (6, 6.4, .12 + .13 * index), (1.6, 1.1, .035), strength_material(f'File plate {index}', keys, .9))
    # Devices: a solid block whose slot answers.
    W.box('Device', (8.9, 0, .55), (1.4, 1.4, 1.1), W.shared('block'))
    W.box('Device slot', (8.19, 0, .55), (.02, .9, .05), strength_material('Device slot', [(0, 0), (7.8, 0), (8.0, 5), (9, .6), (11, .6), (11.2, 6), (12, 2)]))
    # Pipes: an open channel with light running through it.
    for side in (-1, 1):
        W.box(f'Pipe wall {side}', (8.6, -4 + side * .5, .35), (6, .14, .7), W.shared('frame'))
    W.route('Pipe flow', [(5.6, -4), (11.6, -4)], ROUTE, [(0, 0, 0), (9.0, 0, 0), (9.8, 0, 1), (10.6, .7, 1), (11.0, 0, 1)], inlay=False)
    W.route('Response', [(5.6, 4.0), (2.0, 4.0), (2.0, .15), (-18, .15)], ROUTE * .5,
            [(0, 0, 0), (3.0, 0, 0), (3.2, 0, .05), (4.4, .95, 1), (4.5, 1, 1)], inlay=False)
    # Engraved in the floor beside each form, like the application filename.
    for copy_id, center in [('files', (6, 5.45, .004)), ('devices', (8.9, -1.05, .004)), ('pipes', (8.6, -4.95, .004))]:
        W.copy(copy_id, center, .2, upright=False, keys=fade(1.0))
    W.copy('data', (-6, -.45, .004), .14, upright=False, keys=fade(.4))


def opensource():
    """Slabs separate around a seam of light, leaving negative space for the line."""
    W.floor()
    W.haze()
    W.lights([["Backlight", [3, 22, 9], [0, 4, 1], 1400, 8], ["Low rim", [-14, -2, 1.2], [0, 0, .6], 200, 3]])
    W.box('Seam light', (0, 0, .002), (15, 15, .002), strength_material('Seam light', [(0, 1.2)]))
    tile = 3
    for i in range(-2, 3):
        for j in range(-2, 3):
            seed = ((i + 3) * 7 + (j + 3) * 3) % 9 / 8
            slab = W.box(f'Open slab {i},{j}', (i * tile, j * tile, .25), (tile - .03, tile - .03, .5), W.floor_material)
            base = Vector((i * tile, j * tile, .25))
            apart = Vector((i * tile * 1.14, j * tile * 1.14, .25 + .2 + 1.0 * seed))
            W.key(slab, 'location', [(0, base), (.6 + .05 * (abs(i) + abs(j)), base), (2.6, apart), (7.2, apart), (10.6, base)])
            smooth_animation(slab)
    W.copy('open', (0, 4, 2.9), .8, keys=fade(3.0, 6.6))


def power():
    execution('power')


SETS = {'recognition': recognition, 'foundation': foundation, 'field': field, 'execution': execution,
        'proof': proof, 'embedded': embedded, 'namespace': namespace, 'opensource': opensource, 'power': power}
SETS[shot['set']]()
W.camera(shot['camera'])
W.finish()
output = ROOT / 'output/launch-film' / f'review-{config["review"]}' / 'shots' / shot['id']
W.render(output, args.still, W.scene.frame_start)
