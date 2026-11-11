"""Launch film shots (scenario draft 3). Each shot builds one set in set time.

Usage: blender --background --factory-startup --python blender/scripts/launch_film.py --
       --shot 03b-devices [--still 120] [--samples 8] [--device cuda]

Every light is a file write: routes are paths, endpoints are devices. Speeds,
pauses, counts and abstract forms are artwork; the mark, measured strokes,
commands and captures come from official sources. Surfaces whose capture is
not recorded yet stay dark and carry an engraved PLACEHOLDER label.
"""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from film_world import ROOT, World, catalog_file, ripple, smooth_animation  # noqa: E402

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--shot', required=True)
parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='auto')
parser.add_argument('--still', type=int, action='append', help='Set-time frame numbers')
parser.add_argument('--samples', type=int)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
config = json.loads((ROOT / 'productions/launch-film/production.json').read_text())
shot = next(s for s in config['shots'] if s['id'] == args.shot)
look = config['look']
SETS_CONFIG = config.get('sets', {})
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


def typed(start, duration):
    return [(0, 0), (start, 0), (start + duration, 1.02)]


def rise(obj, height, start, duration=.8):
    """Move an object up from below the floor into place."""
    x, y, final = obj.location
    W.key(obj, 'location', [(0, (x, y, final - height)), (start, (x, y, final - height)),
                            (start + duration, (x, y, final))])
    smooth_animation(obj)


def strength_material(name, keys, value=1.0):
    mat, shader = W.emission(name, value, 0)
    W.key_socket(shader.inputs['Strength'], keys, mat.node_tree)
    return mat


def footage_screen(name, entries, strength_keys=((0, 1),)):
    """A glass face showing genuine recordings: [(footage key, set time), ...].
    Later entries take over at their start. None means the capture is pending."""
    screen = W.screen_material(name, None, strength_keys)
    nodes, links = screen.node_tree.nodes, screen.node_tree.links
    if not entries:
        nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 0
        screen.node_tree.animation_data_clear()
        return screen, False
    result = None
    for key, at in entries:
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
        result = mix.outputs['Result']
    links.new(result, nodes['Principled BSDF'].inputs['Emission Color'])
    return screen, True


def pending(center, height=.12, yaw=0.0):
    """Engraved, honest marker for a capture that is not recorded yet."""
    return W.copy('pending', center, height, upright=False, yaw=yaw, keys=[(0, .9)])


def surface(name, x, y, width, entries, strength_keys=((0, 1),), aspect=1.6, yaw=0.0):
    screen, real = footage_screen(f'{name} screen', entries, strength_keys)
    pivot, face = W.monolith(name, x, y, width, aspect, screen=screen, yaw=yaw)
    if not real:
        pending((x, y - .6, .004), width * .03)
    return pivot


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


BOARD = (.045, .018, .0016)  # Arduino Nano 33 BLE outline, abstract


def small(mode='open'):
    """A 45 mm board on an endless floor. One file write switches its LED on."""
    W.floor()
    W.lights([["Board key", [.25, .35, .3], [0, 0, 0], 3, .25], ["Board rim", [-.4, .05, .04], [0, 0, 0], .8, .1]])
    W.box('Board', (0, 0, BOARD[2] / 2), BOARD, W.shared('block'))
    W.box('Module', (-.006, 0, BOARD[2] + .0006), (.01, .01, .0012), W.shared('frame'))
    for i in range(15):  # header pads along both long edges
        for side in (-1, 1):
            W.box(f'Pad {i},{side}', (-.0178 + i * .00254, side * .0078, BOARD[2] + .00005), (.0012, .0012, .0001), W.shared('frame'))
    if mode == 'open':
        led_keys = [(0, 0), (6.2, 0), (6.3, 60)]
        W.route('First route', [(.012, .002), (.012, .02), (.012, 60)], .003, [(0, 0, 0), (6.4, 0, 0), (9.5, 0, .5), (12, 0, 1)], strength=6, inlay=False, light_z=.0001)
        W.copy('cmd_led', (0, .016, .011), .0032, keys=[(0, 0), (3.0, 0), (3.2, 1)], reveal=typed(3.4, 1.8))
        W.copy('kib', (0, .9, .2), .045, yaw=facing((0, .9), (.3, -1.6)), keys=fade(8.0))
        W.copy('complete', (0, .9, .135), .028, yaw=facing((0, .9), (.3, -1.6)), keys=fade(9.6))
    else:  # one light: routes from every passage drain back into the LED
        led_keys = [(0, 60), (8.6, 60), (9.6, 120)]
        for index, angle in enumerate(range(0, 360, 45)):
            a = math.radians(angle)
            far = (math.cos(a) * 40, math.sin(a) * 40)
            W.route(f'Return {index}', [far, (math.cos(a) * .03, math.sin(a) * .03)], .003,
                    [(0, 0, 1), (1.0 + .4 * index, 0, 1), (5.5 + .3 * index, .999, 1), (6 + .3 * index, 1, 1)],
                    strength=6, inlay=False, light_z=.0001)
    W.box('LED', (.012, .002, BOARD[2] + .0003), (.0016, .0008, .0006), strength_material('LED', led_keys))


DEVICE_TIMES = {'gpio': 3.0, 'nn': 8.6, 'audio': 14.6}


def devices():
    """One route, one junction, three devices that answer differently."""
    W.floor()
    W.haze()
    W.lights([["Backlight", [0, 22, 8], [0, 6, .5], 1800, 8], ["Low rim", [-14, -2, 1.2], [0, 4, .6], 250, 3]])
    W.box('Junction', (0, 0, .18), (.7, .7, .36), W.shared('frame'))
    W.route('Request', [(0, -30), (0, -.4)], ROUTE, [(0, 0, 0), (.3, 0, 0), (2.6, 0, 1)])
    branches = {
        'gpio': stepped((-.4, 0), [(-3.2, 0), (0, 4.4), (-2.4, 0)]),
        'nn': stepped((0, .4), [(0, 7.4)]),
        'audio': stepped((.4, 0), [(3.2, 0), (0, 4.4), (2.4, 0)]),
    }
    for name, points in branches.items():
        keys, end = W.metered(points, DEVICE_TIMES[name], 4.5, .2)
        keys += [(20.8, 0, 1), (21.0, 0, 1)]
        W.route(f'Branch {name}', points, ROUTE * .8, keys)
    # Light: an LED form answers its file.
    W.box('Light plinth', (-6.6, 4.4, .25), (.9, .9, .5), W.shared('block'))
    W.box('Light', (-6.6, 4.4, .56), (.14, .07, .05), strength_material('Light', [(0, 0), (5.5, 0), (5.6, 40), (20.9, 40), (21.2, 90), (22.4, 40)]))
    # Intelligence: Digits recognises a hand-drawn 3 through its neural-network device.
    sets = SETS_CONFIG.get('devices', {})
    surface('Digits surface', 0, 8.6, 4.2, sets.get('nn'), [(0, 0), (10.6, 0), (11.0, 1)])
    # Sound: one held note, drawn as light along a row of bars.
    for i in range(28):
        x = 5.0 + i * .12
        h = .05 + .55 * abs(math.sin(i * .55)) * math.exp(-((i - 14) / 9) ** 2)
        bar = W.box(f'Wave {i}', (x, 4.4, h / 2), (.05, .05, h), strength_material(f'Wave {i}', [(0, 0), (16.8 + i * .01, 0), (17.0 + i * .01, 3), (19.0, 3), (19.6, .3), (20.9, .3), (21.2, 4), (22.4, 1)]))
        bar.name = f'Note {i}'
    paths = [('p_gpio', (-6.6, 3.55, .004)), ('p_nn', (0, 7.75, .004)), ('p_audio', (6.6, 3.55, .004))]
    for copy_id, center in paths:
        W.copy(copy_id, center, .16, upright=False, keys=fade(1.0))
    W.copy('file', (0, 6.0, 3.9), .45, yaw=facing((0, 6.0), (0, -14)), keys=fade(20.6))


def execution():
    """Light leaves the mark along the measured Pixel Painter strokes into the surface."""
    W.floor()
    W.haze()
    W.lights()
    source = json.loads((ROOT / config['strokesFrom']).read_text())
    unit, origin = source['floor']['metresPerPixel'], source['floor']['originPixel']
    mono = source['monolith']
    W.mark(tuple(source['mark']['center']), source['mark']['width'])
    for index, pixels in enumerate(source['strokes']['paths']):
        points = [((x - origin[0]) * unit, -(y - origin[1]) * unit) for x, y in pixels]
        points += [(mono['entryX'][index], points[-1][1]), (mono['entryX'][index], mono['frontY'])]
        keys, _ = W.metered(points, .5 + .14 * index, 4.5, .16)
        W.route(f'Stroke {index + 1}', points, source['strokes']['width'] * unit, keys)
    screen = W.screen_material('Genuine capture', config['captures']['painter'], [(0, 0), (6.8, 0), (7.4, 1)])
    W.monolith('Result surface', mono['centerX'], mono['frontY'], mono['width'], 1.6, screen=screen)
    W.copy('pkg', (2.2, 2.55, .004), .11, upright=False, keys=fade(.8))
    camera = (-9, -15)
    W.copy('wasm', (-1.0, 8.0, 4.3), .3, yaw=facing((-1.0, 8.0), camera), keys=fade(4.4, 9.4))


def travel():
    """One package forks to two runtimes; both draw the same strokes."""
    W.floor()
    W.haze()
    W.lights([["Backlight", [0, 22, 8], [0, 4, 1.5], 1800, 8], ["Low rim", [-14, -2, 1.2], [0, 2, .6], 200, 3]])
    sets = SETS_CONFIG.get('travel', {})
    W.copy('pkg', (0, -2.2, .004), .14, upright=False, keys=fade(.2))
    W.route('Package', [(0, -30), (0, 0)], ROUTE, [(0, 0, .2), (1.0, 0, 1)])
    for side, x, key, label in [(-1, -3.6, 'desktop', 'host_desktop'), (1, 3.6, 'browser', 'host_browser')]:
        W.route(f'Fork {key}', stepped((0, 0), [(x, 0), (0, 3.6)]), ROUTE, [(0, 0, 0), (1.0, 0, 0), (2.0, 0, 1)])
        surface(f'{key} surface', x, 3.6, 5.6, sets.get(key), [(0, 0), (2.0, 0), (2.4, 1)])
        W.copy(label, (x, 2.9, .004), .16, upright=False, keys=fade(1.2))
    W.copy('one', (0, 9, 4.9), .42, yaw=facing((0, 9), (0, -14)), keys=fade(3.0))
    W.copy('every', (0, 9, 4.2), .42, yaw=facing((0, 9), (0, -14)), keys=fade(4.2))


def isolated():
    """A faulty application traps; the shell answers the next line; the world keeps moving."""
    W.floor()
    W.haze()
    W.lights([["Backlight", [4, 22, 8], [4, 4, 1], 1600, 8], ["Low rim", [-14, -2, 1.2], [0, 2, .6], 200, 3]])
    for index, x in enumerate([1.6, 5.4, 9.2]):
        failing = index == 1
        keys = [(0, 0, 0), (.4 + .2 * index, 0, 1)]
        if failing:
            keys += [(3.9, 0, 1), (4.0, .5, 1), (4.05, .5, .52), (4.4, 1, 1)]
        W.route(f'Application {index}', [(x, -20), (x, 3.6)], ROUTE, keys)
        glow = [(0, 0), (.8, .12)] + ([(3.95, .12), (4.0, 1.5), (4.15, 0)] if failing else [])
        W.monolith(f'Application surface {index}', x, 3.6, 3.0, 1.0, screen=W.screen_material(f'App {index}', None, glow))
        if not failing:
            W.route(f'Continuing {index}', [(x, -20), (x, 3.6)], ROUTE * .4,
                    [(0, 0, 0), (4.6, 0, 0), (5.2, 0, .3), (7.0, .6, 1), (7.4, 1, 1), (7.5, 0, 0), (8.1, 0, .3), (10, .6, 1), (10.4, 1, 1)], inlay=False)
    toward = (-2, -12)
    rows = [('cmd_trap', 3.4, typed(1.0, 1.2)), ('cmd_alive', 2.95, typed(4.8, .9)), ('alive', 2.5, [(0, 0), (6.0, 0), (6.05, 1.02)])]
    for copy_id, z, reveal in rows:
        W.copy(copy_id, (-4.2, 6, z), .2, yaw=facing((-4.2, 6), toward), keys=[(0, 1)], reveal=reveal)
    pending((-4.2, 5.2, .004), .08)
    W.copy('fail', (-4.2, 6, 1.75), .3, yaw=facing((-4.2, 6), toward), keys=fade(7.2))
    W.copy('running', (-4.2, 6, 1.25), .3, yaw=facing((-4.2, 6), toward), keys=fade(8.4))
    W.copy('rust', (-4.2, 6, .8), .16, yaw=facing((-4.2, 6), toward), keys=fade(9.8))


def roadmap():
    """New boards dock along the routes; a signed package is checked and opened in place."""
    W.floor()
    W.haze()
    W.lights()
    for index, (x, y) in enumerate([(-6, 3), (-2, 6), (3, 7), (7, 4), (-8, 8)]):
        W.route(f'Network {index}', [(0, -2), (0, 1), (x, 1), (x, y - .5)], ROUTE * .6, [(0, 0, 0), (.4 + .5 * index, 0, 1)])
        board = W.box(f'Board {index}', (x, y, .05), (1.2, .5, .1), W.shared('block'))
        rise(board, .2, 1.0 + .5 * index, .8)
        W.box(f'Board light {index}', (x + .3, y, .105), (.06, .03, .01), strength_material(f'Board light {index}', [(0, 0), (1.9 + .5 * index, 0), (2.0 + .5 * index, 30)]))
    W.route('Delivery', [(-30, -2), (0, -2)], ROUTE, [(0, 0, 0), (6.0, 0, 0), (8.6, .6, 1)])
    package = W.box('Signed package', (0, -2, .06), (.8, .8, .12), W.shared('frame'))
    W.key(package, 'location', [(0, (-30, -2, .06)), (6.0, (-30, -2, .06)), (8.8, (0, -2, .06))])
    W.box('Verification ring', (0, -2, .002), (1.3, 1.3, .002), strength_material('Verification', [(0, 0), (9.0, 0), (9.2, 4), (10, .8)]))
    W.monolith('Installed surface', 0, 1.6, 3.2, 1.6, screen=W.screen_material('Installed', None, [(0, 0), (9.6, 0), (10.2, .12)]))
    W.copy('boards', (-3.5, 10, 4.2), .4, yaw=facing((-3.5, 10), (-6, -14)), keys=fade(2.6, 6.2))
    W.copy('signed', (-3.5, 10, 4.2), .32, yaw=facing((-3.5, 10), (-6, -14)), keys=fade(7.0))


def ending():
    small('end')


SETS = {'recognition': recognition, 'small': small, 'devices': devices, 'execution': execution, 'travel': travel,
        'isolated': isolated, 'roadmap': roadmap, 'ending': ending}
SETS[shot['set']]()
W.camera(shot['camera'])
W.finish()
output = ROOT / 'output/launch-film' / f'review-{config["review"]}' / 'shots' / shot['id']
W.render(output, args.still, W.scene.frame_start)
