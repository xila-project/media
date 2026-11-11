"""Shared world for the launch film: one grounded, black, light-driven space.

Art direction (productions/application-handoff/README.md): a continuous polished
floor, low haze, light as the actor, geometry from real sources, deep blacks and a
low, long camera. Sets build on these helpers; nothing here invents interface or
hardware.
"""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand import sync  # noqa: E402
from cinematic_support import select_device, smooth_animation  # noqa: E402

CATALOG = {a['id']: a for a in json.loads((ROOT / 'assets/catalog.json').read_text())['assets']}


def catalog_file(asset_id):
    asset = CATALOG[asset_id]
    path = ROOT / asset['file']
    if hashlib.sha256(path.read_bytes()).hexdigest() != asset['sha256']:
        raise ValueError(f'Catalog hash mismatch: {asset_id}')
    return path, asset


class World:
    def __init__(self, config, look, duration, device, samples):
        sync()
        self.config, self.look, self.fps = config, look, config['fps']
        bpy.ops.wm.read_factory_settings(use_empty=True)
        scene = self.scene = bpy.context.scene
        scene.render.engine = 'CYCLES'
        self.devices = select_device(scene, device)
        scene.cycles.samples = samples
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
        scene.render.fps = self.fps
        scene.frame_start = 0
        scene.frame_end = round(duration * self.fps) - 1
        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_mode = 'RGB'
        scene.view_settings.view_transform = 'AgX'
        scene.view_settings.look = 'AgX - Medium High Contrast'
        scene.world = bpy.data.worlds.new('Black stage')
        scene.world.use_nodes = True
        scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0
        self._materials = {}

    def frame(self, time):
        return round(time * self.fps)

    def key(self, data, prop, keys, smooth=True):
        """Keyframe (time, value) pairs on a property."""
        for time, value in keys:
            setattr(data, prop, value)
            data.keyframe_insert(prop, frame=self.frame(time))
        if smooth:
            smooth_animation(data.id_data if hasattr(data, 'id_data') and data.id_data else data)

    def key_socket(self, socket, keys, tree):
        for time, value in keys:
            socket.default_value = value
            socket.keyframe_insert('default_value', frame=self.frame(time))
        smooth_animation(tree)

    # --- Materials -------------------------------------------------------
    def principled(self, name, value, roughness, metallic=0.0):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        shader = mat.node_tree.nodes['Principled BSDF']
        shader.inputs['Base Color'].default_value = (value, value, value, 1)
        shader.inputs['Roughness'].default_value = roughness
        shader.inputs['Metallic'].default_value = metallic
        return mat, shader

    def emission(self, name, value=1.0, strength=1.0):
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

    def shared(self, name):
        """Reusable house materials."""
        if name not in self._materials:
            self._materials[name] = {
                'frame': lambda: self.principled('Anodised black', .02, .32, 1)[0],
                'block': lambda: self.principled('Black satin block', .015, .38)[0],
                'inlay': lambda: self.principled('Dark glass inlay', .02, .04)[0],
                'clear-space': lambda: self.emission('Identity clear space', 0, 0)[0],
            }[name]()
        return self._materials[name]

    # --- Environment -----------------------------------------------------
    def floor(self, size=240):
        look = self.look['floor']
        path, _ = catalog_file(look['roughnessAsset'])
        mat, bsdf = self.principled('Polished black stone', .006, .16)
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        coords = nodes.new('ShaderNodeTexCoord')
        mapping = nodes.new('ShaderNodeMapping')
        mapping.inputs['Scale'].default_value = (1 / look['textureMetres'],) * 3
        links.new(coords.outputs['Object'], mapping.inputs['Vector'])
        scan = nodes.new('ShaderNodeTexImage')
        scan.image = bpy.data.images.load(str(path))
        scan.image.colorspace_settings.name = 'Non-Color'
        links.new(mapping.outputs['Vector'], scan.inputs['Vector'])
        rough = nodes.new('ShaderNodeMapRange')
        rough.inputs['To Min'].default_value, rough.inputs['To Max'].default_value = look['roughnessRange']
        links.new(scan.outputs['Color'], rough.inputs['Value'])
        seams = nodes.new('ShaderNodeTexBrick')
        seams.offset = 0
        seams.squash = 1
        for socket, value in [('Scale', 1), ('Brick Width', look['tile']), ('Row Height', look['tile']),
                              ('Mortar Size', .006), ('Mortar Smooth', .5)]:
            seams.inputs[socket].default_value = value
        links.new(coords.outputs['Object'], seams.inputs['Vector'])
        mix = nodes.new('ShaderNodeMix')
        mix.data_type = 'FLOAT'
        links.new(seams.outputs['Fac'], mix.inputs['Factor'])
        mix.inputs['A'].default_value = .4
        links.new(rough.outputs['Result'], mix.inputs['B'])
        links.new(mix.outputs['Result'], bsdf.inputs['Roughness'])
        bpy.ops.mesh.primitive_plane_add(size=size)
        obj = bpy.context.object
        obj.name = 'Foundation floor'
        obj.data.materials.append(mat)
        self.floor_material = mat
        return obj

    def haze(self, density=None):
        mat = bpy.data.materials.new('Haze')
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.remove(nodes['Principled BSDF'])
        volume = nodes.new('ShaderNodeVolumePrincipled')
        volume.inputs['Density'].default_value = self.look['haze'] if density is None else density
        volume.inputs['Anisotropy'].default_value = .45
        mat.node_tree.links.new(volume.outputs[0], nodes['Material Output'].inputs['Volume'])
        return self.box('Haze', (0, 0, 8), (160, 160, 16), mat)

    def area(self, name, position, target, energy, size, size_y=None):
        data = bpy.data.lights.new(name, 'AREA')
        data.energy = energy
        if size_y:
            data.shape = 'RECTANGLE'
            data.size, data.size_y = size, size_y
        else:
            data.size = size
        obj = bpy.data.objects.new(name, data)
        self.scene.collection.objects.link(obj)
        self.aim(obj, position, target)
        return obj

    @staticmethod
    def aim(obj, position, target):
        obj.location = position
        obj.rotation_euler = (Vector(target) - Vector(position)).to_track_quat('-Z', 'Y').to_euler()

    def lights(self, spec=None):
        return [self.area(*entry) for entry in (spec or self.look['lights'])]

    # --- Geometry --------------------------------------------------------
    def box(self, name, center, size, mat):
        bpy.ops.mesh.primitive_cube_add(size=1, location=center)
        obj = bpy.context.object
        obj.name = name
        obj.scale = size
        obj.data.materials.append(mat)
        return obj

    def ribbon(self, name, points, mat, width, z=.0005, closed_caps=True):
        """A flat strip along floor points; bevel_factor_end reveals it by length."""
        curve = bpy.data.curves.new(name, 'CURVE')
        curve.dimensions = '3D'
        curve.bevel_depth = width / 2
        curve.bevel_resolution = 0
        curve.use_fill_caps = closed_caps
        curve.bevel_factor_mapping_end = 'SPLINE'
        curve.bevel_factor_mapping_start = 'SPLINE'
        spline = curve.splines.new('POLY')
        spline.points.add(len(points) - 1)
        for item, p in zip(spline.points, points):
            item.co = (p[0], p[1], p[2] if len(p) > 2 else 0, 1)
        obj = bpy.data.objects.new(name, curve)
        self.scene.collection.objects.link(obj)
        obj.location.z = z
        obj.scale.z = .02
        curve.materials.append(mat)
        return obj

    def route(self, name, points, width, keys, strength=None, light_fraction=.72, inlay=True):
        """An inlaid channel with light advancing along it.

        keys: (time, start, end) fractions of the route length. Returns the light curve.
        """
        if inlay:
            self.ribbon(f'{name} inlay', points, self.shared('inlay'), width)
        mat, _ = self.emission(f'{name} light', 1, strength or self.look['lightStrength'])
        obj = self.ribbon(f'{name} light', points, mat, width * light_fraction, z=.008)
        curve = obj.data
        for time, start, end in keys:
            curve.bevel_factor_start = start
            curve.bevel_factor_end = end
            curve.keyframe_insert('bevel_factor_start', frame=self.frame(time))
            curve.keyframe_insert('bevel_factor_end', frame=self.frame(time))
        smooth_animation(curve)
        return obj

    def metered(self, points, start, speed, pause, minimum=.25):
        """Advance-and-pause keys at each corner: editorial fuel slices."""
        lengths = [(Vector(b[:2]) - Vector(a[:2])).length for a, b in zip(points, points[1:])]
        total = sum(lengths)
        time, travelled, keys = start, 0, [(0, 0, 0), (start, 0, 0)]
        for length in lengths:
            travelled += length
            time += max(length / speed, minimum)
            keys.append((time, 0, travelled / total))
            time += pause
            keys.append((time, 0, travelled / total))
        return keys, time - pause

    def mark(self, center, width, z=.006, extrude=0.0, mat=None, plate=True):
        """Import the official five-part SVG; optional shallow perpendicular extrusion."""
        before = set(self.scene.objects)
        bpy.ops.import_curve.svg(filepath=str(ROOT / 'assets/brand/upstream/assets/symbol/xila-symbol-white.svg'))
        curves = [o for o in self.scene.objects if o not in before and o.type == 'CURVE']
        if len(curves) != 5:
            raise ValueError('Expected five official SVG modules')
        corners = [o.matrix_world @ Vector(c) for o in curves for c in o.bound_box]
        low = Vector(tuple(min(p[i] for p in corners) for i in range(3)))
        high = Vector(tuple(max(p[i] for p in corners) for i in range(3)))
        factor = width / (high.x - low.x)
        mat = mat or self.emission('Official white mark', 1, self.look['markStrength'])[0]
        for o in curves:
            o.location = (o.location - (low + high) / 2) * factor + Vector((center[0], center[1], z))
            o.scale *= factor
            # Extrusion is perpendicular to the original paths; no bevel alters the outline.
            o.data.extrude = extrude / factor if extrude else 0
            o.data.bevel_depth = 0
            o.data.resolution_u = 24
            o.data.materials.clear()
            o.data.materials.append(mat)
        if plate:
            side = width * self.look['markPlate']
            if side < width * 1.5:
                raise ValueError('Plate must reserve a quarter-width clear space')
            self.box('Identity plate', (center[0], center[1], .002), (side, side, .004), self.shared('clear-space'))
        return curves

    def screen_material(self, name, asset_id=None, strength_keys=((0, 1),)):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        glass = nodes['Principled BSDF']
        glass.inputs['Base Color'].default_value = (.004, .004, .004, 1)
        glass.inputs['Roughness'].default_value = .02
        if asset_id:
            path, _ = catalog_file(asset_id)
            image = nodes.new('ShaderNodeTexImage')
            image.image = bpy.data.images.load(str(path))
            mat.node_tree.links.new(image.outputs['Color'], glass.inputs['Emission Color'])
            self.screen_image = image
        else:
            glass.inputs['Emission Color'].default_value = (1, 1, 1, 1)
        self.key_socket(glass.inputs['Emission Strength'], strength_keys, mat.node_tree)
        return mat

    def sequence_image(self, directory, start_frame):
        """A retimed, zero-based footage sequence that begins at a set-time frame
        and holds its first and last real frames outside its range."""
        frames = sorted(Path(directory).glob('[0-9]*.png'))
        image = bpy.data.images.load(str(frames[0]))
        image.source = 'SEQUENCE'
        return image, len(frames), start_frame

    @staticmethod
    def bind_sequence(node, image, count, start_frame):
        node.image = image
        user = node.image_user
        user.frame_duration = count
        user.frame_start = start_frame
        user.frame_offset = -1  # first file is 000000
        user.use_auto_refresh = True
        user.use_cyclic = False

    def monolith(self, name, center_x, front_y, width, aspect, base=.25, depth=.3, screen=None, yaw=0.0):
        """A standing surface: plinth, frame and a glass face carrying an image."""
        height = width / aspect
        pivot = bpy.data.objects.new(name, None)
        self.scene.collection.objects.link(pivot)
        pivot.location = (center_x, front_y, 0)
        pivot.rotation_euler.z = yaw
        frame = self.shared('frame')
        parts = [self.box(f'{name} plinth', (0, depth / 2, base / 2), (width + .3, depth + .2, base), frame),
                 self.box(f'{name} body', (0, depth / 2 + .02, base + height / 2), (width + .16, depth, height + .16), frame)]
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -.002, base + height / 2), rotation=(math.pi / 2, 0, 0))
        face = bpy.context.object
        face.name = f'{name} face'
        face.scale = (width, height, 1)
        if screen:
            face.data.materials.append(screen)
        parts.append(face)
        for part in parts:
            part.parent = pivot
        return pivot, face

    def copy(self, copy_id, center, height, yaw=0.0, upright=True, keys=((0, 1),)):
        """Official Montserrat copy as an emissive plane; keys animate its strength."""
        manifest = json.loads((self.copy_dir / 'copy.json').read_text())[copy_id]
        mat = bpy.data.materials.new(f'Copy {copy_id}')
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        image = nodes.new('ShaderNodeTexImage')
        image.image = bpy.data.images.load(str(self.copy_dir / f'{copy_id}.png'))
        shader = nodes.new('ShaderNodeEmission')
        transparent = nodes.new('ShaderNodeBsdfTransparent')
        mix = nodes.new('ShaderNodeMixShader')
        fade = nodes.new('ShaderNodeMath')
        fade.operation = 'MULTIPLY'
        out = nodes.new('ShaderNodeOutputMaterial')
        links = mat.node_tree.links
        links.new(image.outputs['Color'], shader.inputs['Color'])
        links.new(image.outputs['Alpha'], fade.inputs[0])
        links.new(fade.outputs[0], mix.inputs[0])
        links.new(transparent.outputs[0], mix.inputs[1])
        links.new(shader.outputs[0], mix.inputs[2])
        links.new(mix.outputs[0], out.inputs['Surface'])
        shader.inputs['Strength'].default_value = self.look['copyStrength']
        self.key_socket(fade.inputs[1], keys, mat.node_tree)
        # Glyph height is about half the canvas height (160 px type in a 240 px canvas).
        scale = height / .5
        bpy.ops.mesh.primitive_plane_add(size=1, location=center,
                                         rotation=(math.pi / 2 if upright else 0, 0, yaw))
        obj = bpy.context.object
        obj.name = f'Copy: {manifest["text"]}'
        obj.scale = (scale * manifest['width'] / manifest['height'], scale, 1)
        obj.data.materials.append(mat)
        return obj

    # --- Camera ----------------------------------------------------------
    def camera(self, keys, offset=0.0):
        """Quaternion camera keys with depth of field; 'up' may be set per key."""
        data = bpy.data.cameras.new('Camera')
        cam = bpy.data.objects.new('Camera', data)
        self.scene.collection.objects.link(cam)
        self.scene.camera = cam
        data.clip_start, data.clip_end = .02, 300
        data.dof.use_dof = True
        focus = bpy.data.objects.new('Focus', None)
        self.scene.collection.objects.link(focus)
        data.dof.focus_object = focus
        cam.rotation_mode = 'QUATERNION'
        previous = None
        for key in keys:
            frame = self.frame(key['time'] - offset)
            cam.location = key['position']
            forward = (Vector(key['target']) - cam.location).normalized()
            up = Vector(key.get('up', (0, 0, 1)))
            right = forward.cross(up).normalized()
            up = right.cross(forward)
            quat = Matrix((right, up, -forward)).transposed().to_quaternion()
            if previous is not None and previous.dot(quat) < 0:
                quat = Quaternion([-v for v in quat])
            previous = quat
            cam.rotation_quaternion = quat
            data.lens = key['lens']
            data.dof.aperture_fstop = key.get('fstop', 5.6)
            focus.location = key.get('focus', key['target'])
            cam.keyframe_insert('location', frame=frame)
            cam.keyframe_insert('rotation_quaternion', frame=frame)
            data.keyframe_insert('lens', frame=frame)
            data.dof.keyframe_insert('aperture_fstop', frame=frame)
            focus.keyframe_insert('location', frame=frame)
        for item in (cam, data, focus):
            smooth_animation(item)
        return cam

    # --- Finishing and output -------------------------------------------
    def finish(self):
        scene = self.scene
        scene.use_nodes = True
        tree = scene.node_tree
        tree.nodes.clear()
        layers = tree.nodes.new('CompositorNodeRLayers')
        glare = tree.nodes.new('CompositorNodeGlare')
        glare.glare_type = 'BLOOM'
        glare.quality = 'HIGH'
        for name, value in [('Threshold', 1.0), ('Strength', self.look['bloom']), ('Size', 7)]:
            if name in glare.inputs:
                glare.inputs[name].default_value = value
        ellipse = tree.nodes.new('CompositorNodeEllipseMask')
        ellipse.width, ellipse.height = .95, .95
        blur = tree.nodes.new('CompositorNodeBlur')
        blur.size_x = blur.size_y = 300
        blur.filter_type = 'GAUSS'
        vignette = tree.nodes.new('CompositorNodeMixRGB')
        vignette.blend_type = 'MULTIPLY'
        vignette.inputs[0].default_value = self.look['vignette']
        composite = tree.nodes.new('CompositorNodeComposite')
        tree.links.new(layers.outputs['Image'], glare.inputs['Image'])
        tree.links.new(ellipse.outputs['Mask'], blur.inputs['Image'])
        tree.links.new(glare.outputs['Image'], vignette.inputs[1])
        tree.links.new(blur.outputs['Image'], vignette.inputs[2])
        tree.links.new(vignette.outputs['Image'], composite.inputs['Image'])

    def render(self, output, stills=None, start=0):
        scene = self.scene
        (output / 'frames').mkdir(parents=True, exist_ok=True)
        (output / 'stills').mkdir(exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(output / 'scene.blend'))
        if stills:
            for value in stills:
                if not scene.frame_start <= value <= scene.frame_end:
                    raise ValueError('Still frame out of range')
                scene.frame_set(value)
                scene.render.filepath = str(output / 'stills' / f'{value:06d}.png')
                bpy.ops.render.render(write_still=True)
        else:
            scene.frame_start = start
            scene.render.filepath = str(output / 'frames/######')
            bpy.ops.render.render(animation=True)


def ripple(duration, fps, start):
    """Core bootsplash ripple from the shared TypeScript timeline (no Python model)."""
    return json.loads(subprocess.check_output(
        ['node', str(ROOT / 'scripts/bootsplash-keyframes.mjs'), '--duration', str(duration),
         '--fps', str(fps), '--start', str(start)], text=True))
