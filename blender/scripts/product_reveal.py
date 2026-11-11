"""Render replaceable, genuine Xila captures as floating surfaces on a black stage."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from brand import sync  # noqa: E402

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--still', type=int, action='append')
parser.add_argument('--generate-only', action='store_true')
parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='auto')
parser.add_argument('--resolution', choices=['960x540', '1280x720', '1920x1080'])
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
config = json.loads((ROOT / 'productions/product-reveal/production.json').read_text())
if not re.fullmatch(r'[0-9]{3}', config['review']):
    raise ValueError('Review must be a three-digit version')
if args.resolution:
    config['width'], config['height'] = map(int, args.resolution.split('x'))
assets = {asset['id']: asset for asset in json.loads((ROOT / 'assets/catalog.json').read_text())['assets']}
# Resolve every source before touching an earlier rendered review.
for slot in config['screens'].values():
    asset = assets.get(slot['asset'])
    if not asset or asset['kind'] != 'image':
        raise ValueError('Import genuine captures into every screen slot before rendering')
    content = (ROOT / asset['file']).read_bytes()
    if hashlib.sha256(content).hexdigest() != asset['sha256']:
        raise ValueError(f'Screen source hash mismatch: {asset["file"]}')
sync()
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
selected_devices = []
if args.device != 'cpu':
    preferences = bpy.context.preferences.addons['cycles'].preferences
    try:
        preferences.compute_device_type = 'CUDA'
        preferences.get_devices()
        for device in preferences.devices:
            device.use = device.type == 'CUDA'
            if device.use:
                selected_devices.append(device.name)
    except (TypeError, RuntimeError) as error:
        if args.device == 'cuda':
            raise RuntimeError('Requested CUDA device is unavailable') from error
    if selected_devices:
        scene.cycles.device = 'GPU'
    elif args.device == 'cuda':
        raise RuntimeError('Requested CUDA device is unavailable')
print(f'Render device: {scene.cycles.device}; {selected_devices}')
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
scene.view_settings.view_transform = 'Standard'
scene.world = bpy.data.worlds.new('Black stage')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0


def frame(time):
    return round(time * config['fps'])


def smooth_animation(data):
    if data.animation_data and data.animation_data.action:
        for curve in data.animation_data.action.fcurves:
            for key in curve.keyframe_points:
                key.interpolation = 'BEZIER'
                key.handle_left_type = 'AUTO_CLAMPED'
                key.handle_right_type = 'AUTO_CLAMPED'


for panel in config['panels']:
    slot = config['screens'][panel['screen']]
    asset = assets[slot['asset']]
    width = panel['width']
    height = width * slot['height'] / slot['width']
    pivot = bpy.data.objects.new(f'Screen {panel["screen"]}', None)
    scene.collection.objects.link(pivot)
    pivot.location = panel['position']
    pivot.rotation_euler = panel['rotation']
    # A thin neutral surface suggests depth without representing a hardware enclosure.
    bpy.ops.mesh.primitive_cube_add()
    backing = bpy.context.object
    backing.name = f'{panel["screen"]} edge'
    backing.parent = pivot
    backing.scale = (width / 2 + 0.012, height / 2 + 0.012, 0.008)
    backing.location.z = -0.01
    material = bpy.data.materials.new(f'{panel["screen"]} graphite')
    material.diffuse_color = (0.08, 0.08, 0.08, 1)
    material.use_nodes = True
    shader = material.node_tree.nodes['Principled BSDF']
    shader.inputs['Base Color'].default_value = (0.08, 0.08, 0.08, 1)
    shader.inputs['Metallic'].default_value = 0.6
    shader.inputs['Roughness'].default_value = 0.3
    backing.data.materials.append(material)
    # Fit the complete screenshot into the slot, including future sources with another aspect.
    fit = min(width / asset['width'], height / asset['height'])
    bpy.ops.mesh.primitive_plane_add(size=2)
    surface = bpy.context.object
    surface.name = f'{panel["screen"]} genuine capture'
    surface.parent = pivot
    surface.scale = (asset['width'] * fit / 2, asset['height'] * fit / 2, 1)
    surface.location.z = 0.001
    material = bpy.data.materials.new(f'{panel["screen"]} pixels')
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    image = nodes.new('ShaderNodeTexImage')
    image.image = bpy.data.images.load(str(ROOT / asset['file']))
    emission = nodes.new('ShaderNodeEmission')
    output = nodes.new('ShaderNodeOutputMaterial')
    material.node_tree.links.new(image.outputs['Color'], emission.inputs['Color'])
    material.node_tree.links.new(emission.outputs[0], output.inputs['Surface'])
    for time, strength in zip(panel['reveal'], [0, 1]):
        emission.inputs['Strength'].default_value = strength
        emission.inputs['Strength'].keyframe_insert('default_value', frame=frame(time))
    smooth_animation(material.node_tree)
    surface.data.materials.append(material)

# A broad reflection defines the very thin edges, leaving the captures self-lit.
bpy.ops.object.light_add(type='AREA', location=(0, 3, 5))
light = bpy.context.object
light.data.energy = 350
light.data.shape = 'RECTANGLE'
light.data.size = 10
light.data.size_y = 2
light.rotation_euler = (Vector((0, 0, 0)) - light.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add()
camera = bpy.context.object
scene.camera = camera
camera.data.clip_start = 0.05
camera.data.clip_end = 100
for key in config['camera']:
    camera.location = key['position']
    direction = (Vector(key['target']) - camera.location).normalized()
    right = direction.cross(Vector((0, 1, 0))).normalized()
    up = right.cross(direction).normalized()
    camera.rotation_euler = Matrix((right, up, -direction)).transposed().to_euler()
    camera.data.lens = key['lens']
    camera.keyframe_insert('location', frame=frame(key['time']))
    camera.keyframe_insert('rotation_euler', frame=frame(key['time']))
    camera.data.keyframe_insert('lens', frame=frame(key['time']))
smooth_animation(camera)
smooth_animation(camera.data)

output = ROOT / 'output/product-reveal' / f'review-{config["review"]}'
(output / 'frames').mkdir(parents=True, exist_ok=True)
(output / 'stills').mkdir(exist_ok=True)
scene.render.filepath = str(output / 'frames/######')
bpy.ops.wm.save_as_mainfile(filepath=str(output / 'scene.blend'))
(output / 'render.json').write_text(json.dumps({**config, 'renderDevice': scene.cycles.device, 'devices': selected_devices}, indent=2) + '\n')
if not args.generate_only:
    if args.still:
        for value in args.still:
            if not scene.frame_start <= value <= scene.frame_end:
                raise ValueError('Still frame outside production range')
            scene.frame_set(value)
            scene.render.filepath = str(output / 'stills' / f'{value:06d}.png')
            bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.render.render(animation=True)
