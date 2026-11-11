"""A concrete application -> Xila -> genuine application-result motion study."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from brand import sync  # noqa: E402
from cinematic_support import camera_pose, select_device, smooth_animation  # noqa: E402

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--device',choices=['auto','cpu','cuda'],default='auto')
parser.add_argument('--still',type=int,action='append')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
config=json.loads((ROOT/'productions/application-handoff/production.json').read_text())
sync()
asset=next(a for a in json.loads((ROOT/'assets/catalog.json').read_text())['assets'] if a['id']==config['screens']['result']['asset'])
if hashlib.sha256((ROOT/asset['file']).read_bytes()).hexdigest()!=asset['sha256']:
    raise ValueError('Result source hash mismatch')
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.render.engine='CYCLES'
devices=select_device(scene,args.device)
scene.cycles.samples=config['samples']
scene.cycles.seed=0
scene.cycles.use_animated_seed=False
scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED'
scene.render.threads=8
scene.render.resolution_x=config['width']
scene.render.resolution_y=config['height']
scene.render.resolution_percentage=100
scene.render.fps=config['fps']
scene.frame_start=0
scene.frame_end=config['duration']*config['fps']-1
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGB'
scene.view_settings.view_transform='AgX'
scene.world=bpy.data.worlds.new('Black stage')
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0

def at(time):return round(time*config['fps'])

def material(name,value,emission=False):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    if emission:
        nodes.clear()
        shader=nodes.new('ShaderNodeEmission')
        shader.inputs['Color'].default_value=(value,value,value,1)
        output=nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(shader.outputs[0],output.inputs['Surface'])
    else:
        shader=nodes['Principled BSDF']
        shader.inputs['Base Color'].default_value=(value,value,value,1)
        shader.inputs['Metallic'].default_value=.65
        shader.inputs['Roughness'].default_value=.3
    return mat

metal=material('Satin graphite',.035)
white=material('White',1,True)
black=material('Black identity clear space',0,True)

def plate(name,position,width,height,depth=.04):
    bpy.ops.mesh.primitive_cube_add(size=1,location=position)
    obj=bpy.context.object
    obj.name=name
    obj.scale=(width,height,depth)
    obj.data.materials.append(metal)
    return obj

carrier=bpy.data.objects.new('Named WebAssembly application',None)
scene.collection.objects.link(carrier)
app=plate('Application artifact',(0,0,0),2.7,1.7)
app.parent=carrier
# Browser-rendered official Montserrat preserves the variable font's glyphs and weights.
bpy.ops.mesh.primitive_plane_add(size=2)
label=bpy.context.object
label.name=config['application']
label.parent=carrier
label.location=(0,0,.03)
label.scale=(1.3,.8,1)
mat=bpy.data.materials.new('Official Montserrat application label')
mat.use_nodes=True
nodes=mat.node_tree.nodes
nodes.clear()
image=nodes.new('ShaderNodeTexImage')
image.image=bpy.data.images.load(str(ROOT/'output/application-handoff'/f'review-{config["review"]}'/'application-label.png'))
transparent=nodes.new('ShaderNodeBsdfTransparent')
emission=nodes.new('ShaderNodeEmission')
output=nodes.new('ShaderNodeOutputMaterial')
mix=nodes.new('ShaderNodeMixShader')
mat.node_tree.links.new(image.outputs['Color'],emission.inputs['Color'])
mat.node_tree.links.new(image.outputs['Alpha'],mix.inputs[0])
mat.node_tree.links.new(transparent.outputs[0],mix.inputs[1])
mat.node_tree.links.new(emission.outputs[0],mix.inputs[2])
mat.node_tree.links.new(mix.outputs[0],output.inputs['Surface'])
label.data.materials.append(mat)
for time,position in [(0,(-3.4,0,.5)),(1,(-3.1,0,.4)),(3.2,(0,0,-.15))]:
    carrier.location=position
    carrier.keyframe_insert('location',frame=at(time))
smooth_animation(carrier)
plate('Xila runtime foundation',(0,0,0),2.25,2.25,.12)
bpy.ops.mesh.primitive_plane_add(size=1,location=(0,0,.065))
identity=bpy.context.object
identity.scale=(2.25,2.25,1)
identity.data.materials.append(black)
bpy.ops.import_curve.svg(filepath=str(ROOT/'assets/brand/upstream/assets/symbol/xila-symbol-white.svg'))
curves=[obj for obj in scene.objects if obj.type=='CURVE']
if len(curves)!=5:
    raise ValueError('Expected five official SVG modules')
points=[obj.matrix_world@Vector(corner) for obj in curves for corner in obj.bound_box]
low=Vector(tuple(min(p[i] for p in points) for i in range(3)))
high=Vector(tuple(max(p[i] for p in points) for i in range(3)))
center=(low+high)/2
factor=1.4/(high.x-low.x)
for obj in curves:
    obj.location=(obj.location-center)*factor+Vector((0,0,.075))
    obj.scale*=factor
    obj.data.materials.clear()
    obj.data.materials.append(white)

# The output is the actual captured Pixel Painter result, shown briefly after processing.
plate('Application result surface',(3.3,0,-.2),2.7,1.75)
bpy.ops.mesh.primitive_plane_add(size=2,location=(3.3,0,-.17))
result=bpy.context.object
result.scale=(1.3,1.3*asset['height']/asset['width'],1)
mat=bpy.data.materials.new('Genuine native-session result')
mat.use_nodes=True
nodes=mat.node_tree.nodes
nodes.clear()
image=nodes.new('ShaderNodeTexImage')
image.image=bpy.data.images.load(str(ROOT/asset['file']))
emission=nodes.new('ShaderNodeEmission')
output=nodes.new('ShaderNodeOutputMaterial')
mat.node_tree.links.new(image.outputs['Color'],emission.inputs['Color'])
mat.node_tree.links.new(emission.outputs[0],output.inputs['Surface'])
for time,strength in [(0,0),(5.1,0),(5.35,.7),(5.9,0)]:
    emission.inputs['Strength'].default_value=strength
    emission.inputs['Strength'].keyframe_insert('default_value',frame=at(time))
result.data.materials.append(mat)
smooth_animation(mat.node_tree)
curve=bpy.data.curves.new('Runtime to graphics response','CURVE')
curve.dimensions='3D'
curve.bevel_depth=.012
curve.bevel_resolution=2
line=curve.splines.new('POLY')
points=[(1.2,0,0),(1.7,0,0),(1.7,-.65,0),(2.8,-.65,-.15),(2.8,0,-.15)]
line.points.add(len(points)-1)
for item,point in zip(line.points,points):
    item.co=(*point,1)
route=bpy.data.objects.new('Graphics response',curve)
scene.collection.objects.link(route)
curve.materials.append(white)
for time,value in [(0,0),(3.3,0),(4.5,1)]:
    curve.bevel_factor_end=value
    curve.keyframe_insert('bevel_factor_end',frame=at(time))
smooth_animation(curve)
for position,energy,size in [((-3,3,5),700,5),((4,-2,4),600,4)]:
    bpy.ops.object.light_add(type='AREA',location=position)
    light=bpy.context.object
    light.data.energy=energy
    light.data.size=size
    light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add()
camera=bpy.context.object
scene.camera=camera
camera.data.clip_start=.03
for key in config['camera']:
    camera_pose(camera,key['position'],key['target'])
    camera.data.lens=key['lens']
    for data,prop in [(camera,'location'),(camera,'rotation_euler'),(camera.data,'lens')]:
        data.keyframe_insert(prop,frame=at(key['time']))
smooth_animation(camera)
smooth_animation(camera.data)
output=ROOT/'output/application-handoff'/f'review-{config["review"]}'
(output/'frames').mkdir(parents=True,exist_ok=True)
(output/'stills').mkdir(exist_ok=True)
scene.render.filepath=str(output/'frames/######')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output/'scene.blend'))
(output/'render.json').write_text(json.dumps({**config,'devices':devices},indent=2)+'\n')
if args.still:
    for value in args.still:
        if not scene.frame_start<=value<=scene.frame_end:raise ValueError('Still frame out of range')
        scene.frame_set(value)
        scene.render.filepath=str(output/'stills'/f'{value:06d}.png')
        bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
