"""A kinetic, conceptual Rust/runtime/application structure with a brief real app illustration."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand import sync  # noqa: E402
from cinematic_support import camera_pose, select_device, smooth_animation  # noqa: E402

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='auto')
parser.add_argument('--still', type=int, action='append')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
config = json.loads((ROOT / 'productions/architecture-reveal/production.json').read_text())
if not re.fullmatch(r'[0-9]{3}', config['review']):
    raise ValueError('Review must be a three-digit version')
sync()
assets = json.loads((ROOT / 'assets/catalog.json').read_text())['assets']
asset = next(item for item in assets if item['id'] == config['screens']['application']['asset'])
if hashlib.sha256((ROOT / asset['file']).read_bytes()).hexdigest() != asset['sha256']:
    raise ValueError('Application illustration hash mismatch')
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
devices = select_device(scene, args.device)
scene.cycles.samples = config['samples']
scene.cycles.seed = 0
scene.cycles.use_animated_seed = False
scene.cycles.use_denoising = True
scene.render.threads_mode = 'FIXED'
scene.render.threads = 8
scene.render.resolution_x = config['width']
scene.render.resolution_y = config['height']
scene.render.resolution_percentage = 100
scene.render.fps = config['fps']
scene.frame_start = 0
scene.frame_end = config['duration'] * config['fps'] - 1
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.view_settings.view_transform = 'AgX'
scene.world = bpy.data.worlds.new('Black stage')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0


def at(time):
    return round(time * config['fps'])


def material(name, value, emissive=False):
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    nodes = result.node_tree.nodes
    if emissive:
        nodes.clear()
        shader = nodes.new('ShaderNodeEmission')
        shader.inputs['Color'].default_value = (value, value, value, 1)
        output = nodes.new('ShaderNodeOutputMaterial')
        result.node_tree.links.new(shader.outputs[0], output.inputs['Surface'])
    else:
        shader = nodes['Principled BSDF']
        shader.inputs['Base Color'].default_value = (value, value, value, 1)
        shader.inputs['Metallic'].default_value = .7
        shader.inputs['Roughness'].default_value = .27
    return result


metal = material('Graphite', .035)
white = material('White signal', 1, True)
edge = material('Quiet edges', .35, True)


def box(name, position, size, shader):
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    obj.data.materials.append(shader)
    return obj


def path(name, points, shader, radius=.012):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    line = curve.splines.new('POLY')
    line.points.add(len(points) - 1)
    for item, point in zip(line.points, points):
        item.co = (*point, 1)
    obj = bpy.data.objects.new(name, curve)
    scene.collection.objects.link(obj)
    curve.materials.append(shader)
    return obj


def arrive(obj, destination, start, offset, duration=.7):
    obj.location = Vector(destination) + Vector(offset)
    obj.scale *= .01
    obj.keyframe_insert('location', frame=at(start))
    obj.keyframe_insert('scale', frame=at(start))
    obj.location = destination
    obj.scale *= 100
    obj.keyframe_insert('location', frame=at(start + duration))
    obj.keyframe_insert('scale', frame=at(start + duration))
    smooth_animation(obj)


for index, layer in enumerate(config['layers']):
    center = Vector(layer['center'])
    # Separate material forms communicate foundation, runtime routes and application modules.
    for row in range(3):
        for column in range(4):
            position = center + Vector(((column - 1.5) * .66, (row - 1) * .66, 0))
            size = (.6, .6, [.42, .055, .32][index])
            obj = box(f'{layer["label"]} module {row}-{column}', position, size, metal)
            arrive(obj, position, layer['arrival'] + (row + column) * .055,
                   ((0, 0, .55) if index == 0 else (-.4, .4, 1.6)), .68)
            # Four short rails on each module keep the geometry crisp under restrained light.
            rail = path(f'{obj.name} rim', [(-.3,-.3,.08),(.3,-.3,.08),(.3,.3,.08),(-.3,.3,.08),(-.3,-.3,.08)], edge, .006)
            rail.parent = obj
            # Parent scale transforms the local rail; compensate for the tile's dimensions.
            rail.scale = tuple(1 / value for value in size)
# The official mark anchors the abstract structure to Xila without drawing another logo.
bpy.ops.import_curve.svg(filepath=str(ROOT / 'assets/brand/upstream/assets/symbol/xila-symbol-white.svg'))
curves = [obj for obj in scene.objects if obj.type == 'CURVE' and obj.data.dimensions != '3D']
if len(curves) != 5:
    raise ValueError('Expected the five official SVG modules')
points = [obj.matrix_world @ Vector(corner) for obj in curves for corner in obj.bound_box]
low = Vector(tuple(min(point[axis] for point in points) for axis in range(3)))
high = Vector(tuple(max(point[axis] for point in points) for axis in range(3)))
center = (low + high) / 2
factor = 1.15 / (high.x - low.x)
# A quiet backing reserves the official quarter-width clear space around the settled mark.
bpy.ops.mesh.primitive_plane_add(size=1, location=(0,0,.232))
backing = bpy.context.object
backing.name = 'Brand clear space'
backing.scale = (1.8,1.8,1)
backing.data.materials.append(material('Black identity backing', 0, True))
logo_material = material('Official Xila mark', 1, True)
strength = logo_material.node_tree.nodes.get('Emission').inputs['Strength']
for time, value in [(0,0),(.65,0),(1.15,1)]:
    strength.default_value = value
    strength.keyframe_insert('default_value', frame=at(time))
for obj in curves:
    obj.location = (obj.location - center) * factor + Vector((0,0,.24))
    obj.scale *= factor
    obj.data.materials.clear()
    obj.data.materials.append(logo_material)

# Parallel channels are conceptual instruction routes, not measured task counts or bus topology.
for level in range(2):
    left = Vector(config['layers'][level]['center'])
    right = Vector(config['layers'][level + 1]['center'])
    for track in range(3):
        y = (track - 1) * .42
        points = [left + Vector((1.45,y,.24)), left + Vector((1.9,y,.24)),
                  Vector((1.9,right.y + y,right.z + .1)), right + Vector((1.45,y,.1))]
        route = path(f'Route {level}-{track}', points, edge, .01)
        route.data.bevel_factor_end = 0
        route.data.keyframe_insert('bevel_factor_end', frame=at(1.1 + level * 1.4 + track * .06))
        route.data.bevel_factor_end = 1
        route.data.keyframe_insert('bevel_factor_end', frame=at(2.1 + level * 1.4 + track * .06))
        smooth_animation(route.data)
        distances = [0]
        for previous, current in zip(points, points[1:]):
            distances.append(distances[-1] + (current - previous).length)
        for lap in range(3):
            pulse = box(f'Signal {level}-{track}-{lap}', points[0], (.1,.06,.06), white)
            start = 1.8 + level * 1.4 + track * .11 + lap * .65
            for point, distance in zip(points, distances):
                pulse.location = point
                pulse.keyframe_insert('location', frame=at(start + distance / distances[-1] * .75))
            pulse.hide_render = True
            pulse.keyframe_insert('hide_render', frame=at(start) - 1)
            pulse.hide_render = False
            pulse.keyframe_insert('hide_render', frame=at(start))
            pulse.keyframe_insert('hide_render', frame=at(start + .75))
            pulse.hide_render = True
            pulse.keyframe_insert('hide_render', frame=at(start + .75) + 1)
            for curve in pulse.animation_data.action.fcurves:
                for key in curve.keyframe_points:
                    key.interpolation = 'LINEAR' if curve.data_path == 'location' else 'CONSTANT'

# A single real Wasm application is a brief illustration within the application layer.
center = Vector(config['layers'][2]['center'])
bpy.ops.mesh.primitive_plane_add(size=2, location=center + Vector((0, 0, .25)))
illustration = bpy.context.object
illustration.name = 'Actual Pixel Painter session'
illustration.scale = (1.18, 1.18 * asset['height'] / asset['width'], 1)
shader = bpy.data.materials.new('Application illustration')
shader.use_nodes = True
nodes = shader.node_tree.nodes
nodes.clear()
image = nodes.new('ShaderNodeTexImage')
image.image = bpy.data.images.load(str(ROOT / asset['file']))
emission = nodes.new('ShaderNodeEmission')
output = nodes.new('ShaderNodeOutputMaterial')
shader.node_tree.links.new(image.outputs['Color'], emission.inputs['Color'])
shader.node_tree.links.new(emission.outputs[0], output.inputs['Surface'])
for time, strength in [(0,0),(config['illustration']['start'],0),(config['illustration']['peak'],.65),(config['illustration']['end'],0)]:
    emission.inputs['Strength'].default_value = strength
    emission.inputs['Strength'].keyframe_insert('default_value', frame=at(time))
smooth_animation(shader.node_tree)
illustration.data.materials.append(shader)
# Hide the black plane outside the brief illustration, so it cannot cover the module animation.
for time, hidden in [(0,True),(config['illustration']['start'],False),(config['illustration']['end'],True)]:
    illustration.hide_render = hidden
    illustration.keyframe_insert('hide_render', frame=at(time))

for name, position, energy, size in [('Key',(-3,-4,8),800,7),('Rim',(4,3,6),700,5)]:
    bpy.ops.object.light_add(type='AREA', location=position)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.size = size
    light.rotation_euler = (Vector((0,0,1)) - light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add()
camera = bpy.context.object
scene.camera = camera
camera.data.clip_start = .03
focus = bpy.data.objects.new('Camera focus', None)
scene.collection.objects.link(focus)
camera.data.dof.use_dof = True
camera.data.dof.focus_object = focus
camera.data.dof.aperture_fstop = 5.6
for key in config['camera']:
    camera_pose(camera, key['position'], key['target'], (0,0,1))
    focus.location = key['target']
    camera.data.lens = key['lens']
    for data, prop in [(camera,'location'),(camera,'rotation_euler'),(camera.data,'lens'),(focus,'location')]:
        data.keyframe_insert(prop, frame=at(key['time']))
for data in [camera,camera.data,focus]:
    smooth_animation(data)

output = ROOT / 'output/architecture-reveal' / f'review-{config["review"]}'
(output / 'frames').mkdir(parents=True, exist_ok=True)
(output / 'stills').mkdir(exist_ok=True)
scene.render.filepath = str(output / 'frames/######')
bpy.ops.wm.save_as_mainfile(filepath=str(output / 'scene.blend'))
(output / 'render.json').write_text(json.dumps({**config,'renderDevice':scene.cycles.device,'devices':devices},indent=2)+'\n')
if args.still:
    for value in args.still:
        if not scene.frame_start <= value <= scene.frame_end:
            raise ValueError('Still frame outside production range')
        scene.frame_set(value)
        scene.render.filepath = str(output / 'stills' / f'{value:06d}.png')
        bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
