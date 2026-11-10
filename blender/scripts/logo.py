"""Deterministic official SVG logo scene. No geometry is approximated or animated."""
import argparse
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from brand import sync  # noqa: E402

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--generate-only', action='store_true')
parser.add_argument('--frame', type=int)
parser.add_argument('--resolution', choices=['1920x1080','1280x720','960x540'])
parser.add_argument('--fps', type=int, choices=[24,30,60])
parser.add_argument('--preset', choices=['fast','medium','slow'], default='fast')
parser.add_argument('--config', type=Path, default=ROOT / 'blender/templates/logo.json')
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
config = json.loads(args.config.read_text())
if args.resolution:
    config['width'],config['height']=map(int,args.resolution.split('x'))
if args.fps:
    config['fps']=args.fps
if args.frame is not None and not 1 <= args.frame <= config['fps']*config['duration']:
    parser.error('Frame is outside the configured sequence')
sync()
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = {'fast':16,'medium':32,'slow':64}[args.preset]
scene.cycles.seed = 0
scene.cycles.use_animated_seed = False
scene.render.resolution_x = config['width']
scene.render.resolution_y = config['height']
scene.render.resolution_percentage = 100
scene.render.fps = config['fps']
scene.render.film_transparent = config['transparent']
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.frame_start = 1
scene.frame_end = config['fps']*config['duration']
scene.world = bpy.data.worlds.new('World')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.1,.1,.1,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .2
# SVG import preserves paths and their relative positions; all modules share one material.
bpy.ops.import_curve.svg(filepath=str(ROOT / 'assets/brand/upstream/assets/symbol/xila-symbol-white.svg'))
curves = [obj for obj in scene.objects if obj.type == 'CURVE']
if not curves:
    raise RuntimeError('Official SVG importer produced no curves')
points = [obj.matrix_world @ Vector(corner) for obj in curves for corner in obj.bound_box]
low = Vector(tuple(min(point[i] for point in points) for i in range(3)))
high = Vector(tuple(max(point[i] for point in points) for i in range(3)))
center = (low + high) / 2
scale = 2 / (high.x-low.x)
material = bpy.data.materials.new('Official white')
material.use_nodes = True
shader = material.node_tree.nodes.get('Principled BSDF')
shader.inputs['Base Color'].default_value = (1,1,1,1)
shader.inputs['Roughness'].default_value = config['materialRoughness']
# The official mark stays flat white; lighting is for other objects added to this template.
emission=material.node_tree.nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value=(1,1,1,1)
emission.inputs['Strength'].default_value=1
material.node_tree.links.new(emission.outputs[0],material.node_tree.nodes['Material Output'].inputs['Surface'])
scene.view_settings.view_transform='Standard'
for obj in curves:
    obj.location = (obj.location-center)*scale
    obj.scale *= scale
    obj.data.extrude = 0  # Keep the core mark flat and faithful.
    obj.data.materials.clear()
    obj.data.materials.append(material)
camera_data = bpy.data.cameras.new('Camera')
camera = bpy.data.objects.new('Camera',camera_data)
scene.collection.objects.link(camera)
camera.location = (0,0,config['cameraDistance'])
camera.data.type = 'ORTHO'
camera.data.ortho_scale = config['orthoScale']
scene.camera = camera
light_data = bpy.data.lights.new('Key',type='AREA')
light_data.energy = config['lightEnergy']
light_data.shape = 'DISK'
light_data.size = 5
light = bpy.data.objects.new('Key',light_data)
scene.collection.objects.link(light)
light.location = (0,0,4)
# Animate camera opacity-independent distance only for perspective scenes derived from this template;
# the official orthographic logo stays unrotated with its original spacing.
output = ROOT / 'output/blender'
output.mkdir(parents=True,exist_ok=True)
scene.render.filepath = str(output / 'frames' / '') + '/'
(output / 'frames').mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(output / 'logo.blend'))
if not args.generate_only:
    if args.frame:
        scene.frame_set(args.frame)
        scene.render.filepath = str(output / 'frames' / f'{args.frame:04d}.png')
        bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.render.render(animation=True)
