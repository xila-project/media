"""Execution study: Xila's light becomes a genuine Pixel Painter drawing.

The three stepped paths inlaid in the floor are the stroke centerlines measured
from the pinned native capture, scaled to architecture. Light leaves the
official mark, advances in metered stages with pauses at each boundary, and
reaches a monolithic surface showing the captured application with the same
drawing. Speeds, pauses and the route extension into the surface are artwork.
"""
import argparse
import hashlib
import json
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
parser.add_argument('--samples', type=int, help='Override samples for quick look checks')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
config = json.loads((ROOT / 'productions/application-handoff/production.json').read_text())
sync()
asset = next(a for a in json.loads((ROOT / 'assets/catalog.json').read_text())['assets']
             if a['id'] == config['screens']['result']['asset'])
if hashlib.sha256((ROOT / asset['file']).read_bytes()).hexdigest() != asset['sha256']:
    raise ValueError('Result source hash mismatch')
output = ROOT / 'output/application-handoff' / f'review-{config["review"]}'

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
devices = select_device(scene, args.device)
scene.cycles.samples = args.samples or config['samples']
scene.cycles.seed = 0
scene.cycles.use_animated_seed = False
scene.cycles.use_denoising = True
scene.cycles.volume_step_rate = 4
scene.cycles.max_bounces = 6
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
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.world = bpy.data.worlds.new('Black stage')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0


def at(time):
    return round(time * config['fps'])


def principled(name, value, roughness, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes['Principled BSDF']
    shader.inputs['Base Color'].default_value = (value, value, value, 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metallic
    return mat, shader


def emission(name, value, strength=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    shader = nodes.new('ShaderNodeEmission')
    shader.inputs['Color'].default_value = (value, value, value, 1)
    shader.inputs['Strength'].default_value = strength
    out = nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(shader.outputs[0], out.inputs['Surface'])
    return mat, shader


def box(name, center, size, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    obj.data.materials.append(mat)
    return obj


def image_material(name, path, strength):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    image = nodes.new('ShaderNodeTexImage')
    image.image = bpy.data.images.load(str(path))
    shader = nodes.new('ShaderNodeEmission')
    shader.inputs['Strength'].default_value = strength
    transparent = nodes.new('ShaderNodeBsdfTransparent')
    mix = nodes.new('ShaderNodeMixShader')
    out = nodes.new('ShaderNodeOutputMaterial')
    links = mat.node_tree.links
    links.new(image.outputs['Color'], shader.inputs['Color'])
    links.new(image.outputs['Alpha'], mix.inputs[0])
    links.new(transparent.outputs[0], mix.inputs[1])
    links.new(shader.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], out.inputs['Surface'])
    return mat, shader


# --- Floor: one continuous polished black surface. The CC0 roughness scan gives
# it uneven, physical reflections; seams are barely visible architectural joints.
floor_cfg = config['floor']
rough_asset = next(a for a in json.loads((ROOT / 'assets/catalog.json').read_text())['assets']
                   if a['id'] == floor_cfg['roughnessAsset'])
floor_mat, floor_bsdf = principled('Polished black stone', .006, .16)
nodes, links = floor_mat.node_tree.nodes, floor_mat.node_tree.links
coords = nodes.new('ShaderNodeTexCoord')
mapping = nodes.new('ShaderNodeMapping')
mapping.inputs['Scale'].default_value = (1 / floor_cfg['textureMetres'],) * 3
links.new(coords.outputs['Object'], mapping.inputs['Vector'])
scan = nodes.new('ShaderNodeTexImage')
scan.image = bpy.data.images.load(str(ROOT / rough_asset['file']))
scan.image.colorspace_settings.name = 'Non-Color'
links.new(mapping.outputs['Vector'], scan.inputs['Vector'])
rough = nodes.new('ShaderNodeMapRange')
rough.inputs['To Min'].default_value, rough.inputs['To Max'].default_value = floor_cfg['roughnessRange']
links.new(scan.outputs['Color'], rough.inputs['Value'])
seams = nodes.new('ShaderNodeTexBrick')
seams.offset = 0
seams.squash = 1
seams.inputs['Scale'].default_value = 1
seams.inputs['Brick Width'].default_value = floor_cfg['tile']
seams.inputs['Row Height'].default_value = floor_cfg['tile']
seams.inputs['Mortar Size'].default_value = .006
seams.inputs['Mortar Smooth'].default_value = .5
links.new(coords.outputs['Object'], seams.inputs['Vector'])
seam_rough = nodes.new('ShaderNodeMix')
seam_rough.data_type = 'FLOAT'
links.new(seams.outputs['Fac'], seam_rough.inputs['Factor'])
seam_rough.inputs['A'].default_value = .4
links.new(rough.outputs['Result'], seam_rough.inputs['B'])
links.new(seam_rough.outputs['Result'], floor_bsdf.inputs['Roughness'])
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
floor = bpy.context.object
floor.name = 'Foundation floor'
floor.data.materials.append(floor_mat)

# Low haze gives the light volume without visible effects.
haze_mat = bpy.data.materials.new('Haze')
haze_mat.use_nodes = True
haze_nodes = haze_mat.node_tree.nodes
haze_nodes.remove(haze_nodes['Principled BSDF'])
volume = haze_nodes.new('ShaderNodeVolumePrincipled')
volume.inputs['Density'].default_value = config['haze']
volume.inputs['Anisotropy'].default_value = .45
haze_mat.node_tree.links.new(volume.outputs[0], haze_nodes['Material Output'].inputs['Volume'])
box('Haze', (0, 0, 6), (60, 60, 12), haze_mat)

# --- Stroke geometry from the genuine capture, mapped to floor metres.
strokes = config['strokes']
unit = config['floor']['metresPerPixel']
origin = config['floor']['originPixel']


def floor_point(p):
    return ((p[0] - origin[0]) * unit, -(p[1] - origin[1]) * unit)


monolith = config['monolith']
entry_y = monolith['frontY']
paths = []
for index, pixels in enumerate(strokes['paths']):
    points = [floor_point(p) for p in pixels]
    # Artwork extension: each route steps once more into the surface base.
    turn = monolith['entryX'][index]
    points += [(turn, points[-1][1]), (turn, entry_y)]
    paths.append(points)

inlay_mat, _ = principled('Dark glass inlay', .02, .04)
light_mat, light_shader = emission('Execution light', 1, config['lightStrength'])
width = strokes['width'] * unit


def ribbon(name, points, mat, z, fraction=1.0):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = width * fraction / 2
    curve.bevel_resolution = 0
    curve.use_fill_caps = True
    curve.bevel_factor_mapping_end = 'SPLINE'  # length along the spline
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for item, (x, y) in zip(spline.points, points):
        item.co = (x, y, 0, 1)
    obj = bpy.data.objects.new(name, curve)
    scene.collection.objects.link(obj)
    obj.location.z = z
    obj.scale.z = .02
    curve.materials.append(mat)
    return curve


timing = config['execution']
arrivals = []
for index, points in enumerate(paths):
    ribbon(f'Stroke {index + 1} inlay', points, inlay_mat, .0005)
    lit = ribbon(f'Stroke {index + 1} execution', points, light_mat, .008, config['lightWidth'])
    lengths = [(Vector(b) - Vector(a)).length for a, b in zip(points, points[1:])]
    total = sum(lengths)
    time = timing['start'] + index * timing['stagger']
    travelled = 0
    keys = [(time, 0)]
    # Metered cooperative slices: advance to a boundary, pause, resume.
    for length in lengths:
        travelled += length
        time += max(length / timing['speed'], timing['minimumSegment'])
        keys.append((time, travelled / total))
        time += timing['pause']
        keys.append((time, travelled / total))
    arrivals.append(keys[-1][0] - timing['pause'])
    lit.bevel_factor_end = 0
    lit.keyframe_insert('bevel_factor_end', frame=0)
    for t, value in keys:
        lit.bevel_factor_end = value
        lit.keyframe_insert('bevel_factor_end', frame=at(t))
    smooth_animation(lit)
arrival = max(arrivals)
print(f'Execution arrival at {arrival:.2f}s')

# --- The official mark as the source, inlaid on its black clear-space plate.
mark = config['mark']
plate_mat, _ = emission('Identity clear space', 0, 0)
box('Identity plate', (*mark['center'], .002), (mark['plate'], mark['plate'], .004), plate_mat)
bpy.ops.import_curve.svg(filepath=str(ROOT / 'assets/brand/upstream/assets/symbol/xila-symbol-white.svg'))
curves = [obj for obj in scene.objects if obj.type == 'CURVE' and obj.data.splines and obj.data.bevel_depth == 0]
if len(curves) != 5:
    raise ValueError('Expected five official SVG modules')
corners = [obj.matrix_world @ Vector(c) for obj in curves for c in obj.bound_box]
low = Vector(tuple(min(p[i] for p in corners) for i in range(3)))
high = Vector(tuple(max(p[i] for p in corners) for i in range(3)))
factor = mark['width'] / (high.x - low.x)
mark_mat, _ = emission('Official white mark', 1, mark['strength'])
for obj in curves:
    obj.location = (obj.location - (low + high) / 2) * factor + Vector((*mark['center'], .006))
    obj.scale *= factor
    obj.data.materials.clear()
    obj.data.materials.append(mark_mat)
if mark['plate'] < mark['width'] * 1.5:
    raise ValueError('Plate does not reserve a quarter-width clear space')

# --- Monolithic surface carrying the genuine captured application.
frame_mat, _ = principled('Anodised black frame', .02, .32, 1)
w, h, d = monolith['width'], monolith['height'], monolith['depth']
cx, base = monolith['centerX'], monolith['base']
front = entry_y
box('Surface plinth', (cx, front + d / 2, base / 2), (w + .3, d + .2, base), frame_mat)
box('Surface body', (cx, front + d / 2 + .02, base + h / 2), (w + .16, d, h + .16), frame_mat)
screen_w = w
screen_h = w * asset['height'] / asset['width']
bpy.ops.mesh.primitive_plane_add(size=1, location=(cx, front - .002, base + h / 2), rotation=(1.5708, 0, 0))
screen = bpy.context.object
screen.name = 'Genuine Pixel Painter capture'
screen.scale = (screen_w, screen_h, 1)
mat = bpy.data.materials.new('Captured result behind glass')
mat.use_nodes = True
nodes = mat.node_tree.nodes
glass = nodes['Principled BSDF']
glass.inputs['Base Color'].default_value = (.004, .004, .004, 1)
glass.inputs['Roughness'].default_value = .02
image = nodes.new('ShaderNodeTexImage')
image.image = bpy.data.images.load(str(ROOT / asset['file']))
links = mat.node_tree.links
links.new(image.outputs['Color'], glass.inputs['Emission Color'])
strength = glass.inputs['Emission Strength']
reveal = config['reveal']
for t, value in [(0, 0), (arrival + reveal['delay'], 0), (arrival + reveal['delay'] + reveal['duration'], reveal['strength'])]:
    strength.default_value = value
    strength.keyframe_insert('default_value', frame=at(t))
screen.data.materials.append(mat)
smooth_animation(mat.node_tree)

label_mat, _ = image_material('Engraved application filename', output / 'application-label.png', config['labelStrength'])
bpy.ops.mesh.primitive_plane_add(size=1, location=(*config['label']['center'], .004))
label = bpy.context.object
label.name = config['application']
label.scale = (config['label']['width'], config['label']['width'] / 8, 1)
label.data.materials.append(label_mat)

# --- Lighting: one broad backlight for floor sheen and haze, one low rim.
for name, position, target, energy, size in config['lights']:
    bpy.ops.object.light_add(type='AREA', location=position)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.size = size
    light.rotation_euler = (Vector(target) - Vector(position)).to_track_quat('-Z', 'Y').to_euler()

# --- Camera: low and long, then a crane to the composed reveal.
bpy.ops.object.camera_add()
camera = bpy.context.object
scene.camera = camera
camera.data.clip_start = .02
camera.data.dof.use_dof = True
focus = bpy.data.objects.new('Focus', None)
scene.collection.objects.link(focus)
camera.data.dof.focus_object = focus
for key in config['camera']:
    camera_pose(camera, key['position'], key['target'], world_up=(0, 0, 1))
    camera.data.lens = key['lens']
    camera.data.dof.aperture_fstop = key['fstop']
    focus.location = key.get('focus', key['target'])
    frame = at(key['time'])
    for data, prop in [(camera, 'location'), (camera, 'rotation_euler'), (camera.data, 'lens'),
                       (camera.data.dof, 'aperture_fstop'), (focus, 'location')]:
        data.keyframe_insert(prop, frame=frame)
smooth_animation(camera)
smooth_animation(camera.data)
smooth_animation(focus)

# --- Finishing: restrained bloom on the light and a soft vignette.
scene.use_nodes = True
tree = scene.node_tree
tree.nodes.clear()
layers = tree.nodes.new('CompositorNodeRLayers')
glare = tree.nodes.new('CompositorNodeGlare')
glare.glare_type = 'BLOOM'
glare.quality = 'HIGH'
for name, value in [('Threshold', 1.0), ('Strength', config['bloom']), ('Size', 7)]:
    if name in glare.inputs:
        glare.inputs[name].default_value = value
ellipse = tree.nodes.new('CompositorNodeEllipseMask')
ellipse.width, ellipse.height = .95, .95
blur = tree.nodes.new('CompositorNodeBlur')
blur.size_x = blur.size_y = 300
blur.filter_type = 'GAUSS'
vignette = tree.nodes.new('CompositorNodeMixRGB')
vignette.blend_type = 'MULTIPLY'
vignette.inputs[0].default_value = config['vignette']
composite = tree.nodes.new('CompositorNodeComposite')
tree.links.new(layers.outputs['Image'], glare.inputs['Image'])
tree.links.new(ellipse.outputs['Mask'], blur.inputs['Image'])
tree.links.new(glare.outputs['Image'], vignette.inputs[1])
tree.links.new(blur.outputs['Image'], vignette.inputs[2])
tree.links.new(vignette.outputs['Image'], composite.inputs['Image'])

(output / 'frames').mkdir(parents=True, exist_ok=True)
(output / 'stills').mkdir(exist_ok=True)
scene.render.filepath = str(output / 'frames/######')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / 'scene.blend'))
(output / 'render.json').write_text(json.dumps({**config, 'devices': devices, 'arrival': arrival}, indent=2) + '\n')
if args.still:
    for value in args.still:
        if not scene.frame_start <= value <= scene.frame_end:
            raise ValueError('Still frame out of range')
        scene.frame_set(value)
        scene.render.filepath = str(output / 'stills' / f'{value:06d}.png')
        bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
