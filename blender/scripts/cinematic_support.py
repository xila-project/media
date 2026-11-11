"""Shared Cycles device selection and camera/keyframe operations for cinematic scenes."""
import bpy
from mathutils import Matrix, Vector


def select_device(scene, requested):
    scene.cycles.device = 'CPU'
    selected = []
    if requested != 'cpu':
        preferences = bpy.context.preferences.addons['cycles'].preferences
        try:
            preferences.compute_device_type = 'CUDA'
            preferences.get_devices()
            for device in preferences.devices:
                device.use = device.type == 'CUDA'
                if device.use:
                    selected.append(device.name)
        except (TypeError, RuntimeError) as error:
            if requested == 'cuda':
                raise RuntimeError('Requested CUDA device is unavailable') from error
        if selected:
            scene.cycles.device = 'GPU'
        elif requested == 'cuda':
            raise RuntimeError('Requested CUDA device is unavailable')
    print(f'Render device: {scene.cycles.device}; {selected}')
    return selected


def smooth_animation(data):
    if data.animation_data and data.animation_data.action:
        for curve in data.animation_data.action.fcurves:
            for key in curve.keyframe_points:
                key.interpolation = 'BEZIER'
                key.handle_left_type = 'AUTO_CLAMPED'
                key.handle_right_type = 'AUTO_CLAMPED'


def camera_pose(camera, position, target, world_up=(0, 1, 0)):
    camera.location = position
    direction = (Vector(target) - camera.location).normalized()
    right = direction.cross(Vector(world_up)).normalized()
    up = right.cross(direction).normalized()
    camera.rotation_euler = Matrix((right, up, -direction)).transposed().to_euler()
