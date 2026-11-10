"""Cinematic material and camera study using the exact official SVG silhouette.

A shallow extrusion is a production treatment requested for the launch film,
not a replacement brand asset. The settled flat SVG remains the identity master.
"""
import argparse
import json
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from brand import sync  # noqa: E402

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--still',type=int,action='append',help='Render only these zero-based frames')
parser.add_argument('--generate-only',action='store_true')
parser.add_argument('--resolution',choices=['960x540','1280x720','1920x1080'])
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
config=json.loads((ROOT/'productions/cinematic-opening/production.json').read_text())
if args.resolution:
    config['width'],config['height']=map(int,args.resolution.split('x'))
sync()
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.device='CPU'
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
background=scene.world.node_tree.nodes['Background']
background.inputs['Color'].default_value=(0,0,0,1)
background.inputs['Strength'].default_value=0

# Import all five modules together so all official gaps and source transforms survive.
bpy.ops.import_curve.svg(filepath=str(ROOT/'assets/brand/upstream/assets/symbol/xila-symbol-white.svg'))
curves=[obj for obj in scene.objects if obj.type=='CURVE']
if len(curves)!=5:
    raise RuntimeError('Expected five official SVG modules; review the brand update')
points=[obj.matrix_world @ Vector(corner) for obj in curves for corner in obj.bound_box]
low=Vector(tuple(min(p[i] for p in points) for i in range(3)))
high=Vector(tuple(max(p[i] for p in points) for i in range(3)))
center=(low+high)/2
scale=2/(high.x-low.x)
material=bpy.data.materials.new('Neutral satin metal')
material.use_nodes=True
shader=material.node_tree.nodes['Principled BSDF']
value=config['material']['baseColor']
shader.inputs['Base Color'].default_value=(value,value,value,1)
shader.inputs['Metallic'].default_value=config['material']['metallic']
shader.inputs['Roughness'].default_value=config['material']['roughness']
for obj in curves:
    obj.location=(obj.location-center)*scale
    obj.scale*=scale
    # Extrusion is perpendicular to the original paths; no bevel changes their outline.
    obj.data.extrude=config['extrusion']/obj.scale.z
    obj.data.bevel_depth=0
    obj.data.resolution_u=24
    obj.data.materials.clear()
    obj.data.materials.append(material)

focus=bpy.data.objects.new('Focus',None)
scene.collection.objects.link(focus)
camera_data=bpy.data.cameras.new('Camera')
camera=bpy.data.objects.new('Camera',camera_data)
scene.collection.objects.link(camera)
scene.camera=camera
camera_data.clip_start=0.01
camera_data.clip_end=100
camera_data.dof.use_dof=True
camera_data.dof.focus_object=focus
camera_data.dof.aperture_fstop=5.6
camera.rotation_mode='QUATERNION'
for key in config['camera']:
    frame=round(key['time']*config['fps'])
    camera.location=key['position']
    focus.location=key['target']
    forward=(focus.location-camera.location).normalized()
    right=forward.cross(Vector((0,1,0))).normalized()
    up=right.cross(forward)
    # Keep screen-up aligned to world Y; avoid the track helper's pole roll.
    camera.rotation_quaternion=Matrix((right,up,-forward)).transposed().to_quaternion()
    camera_data.lens=key['lens']
    camera.keyframe_insert('location',frame=frame)
    camera.keyframe_insert('rotation_quaternion',frame=frame)
    camera_data.keyframe_insert('lens',frame=frame)
    focus.keyframe_insert('location',frame=frame)


def area(name,position,target,power,size,size_y):
    data=bpy.data.lights.new(name,'AREA')
    data.energy=power
    data.shape='RECTANGLE'
    data.size=size
    data.size_y=size_y
    obj=bpy.data.objects.new(name,data)
    scene.collection.objects.link(obj)
    obj.location=position
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    return obj


# Large physical strip sources form controlled reflections, without bloom or particles.
key=area('Moving strip',(-2.5,0.8,2),(0,0,0),450,3.5,0.18)
for frame,position,power in [(0,(-2.5,0.8,2),0.5),(60,(-1.4,1.1,2.4),250),(125,(0.4,0.8,2.8),450),(180,(1.2,0.9,3.2),700)]:
    key.location=position
    key.rotation_euler=(-key.location).to_track_quat('-Z','Y').to_euler()
    key.data.energy=power
    key.keyframe_insert('location',frame=frame)
    key.keyframe_insert('rotation_euler',frame=frame)
    key.data.keyframe_insert('energy',frame=frame)
edge=area('Edge strip',(1.8,-1.5,1.6),(0,0,0),150,3,0.10)
fill=area('Soft return',(-0.5,-2,3),(0,0,0),50,4,2)
for light,values in [(edge,[(0,0),(45,90),(180,150)]),(fill,[(0,0),(90,15),(180,50)])]:
    for frame,power in values:
        light.data.energy=power
        light.data.keyframe_insert('energy',frame=frame)
# A black world isolates the geometry; there is no invented device, UI or hardware claim.
output=ROOT/'output/cinematic-opening'
output.mkdir(parents=True,exist_ok=True)
(output/'frames').mkdir(exist_ok=True)
(output/'stills').mkdir(exist_ok=True)
scene.render.filepath=str(output/'frames')+'/'
bpy.ops.wm.save_as_mainfile(filepath=str(output/'opening.blend'))
(output/'render.json').write_text(json.dumps(config,indent=2)+'\n')
if not args.generate_only:
    if args.still:
        for frame in args.still:
            if not scene.frame_start<=frame<=scene.frame_end:
                raise ValueError('Still frame outside production range')
            scene.frame_set(frame)
            scene.render.filepath=str(output/'stills'/f'{frame:06d}.png')
            bpy.ops.render.render(write_still=True)
    else:
        # Blender uses four digits by default; six hashes provide the assembly contract.
        scene.render.filepath=str(output/'frames'/'######')
        bpy.ops.render.render(animation=True)
