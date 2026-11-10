"""Validate a headless Blender PNG sequence without importing bpy."""
import argparse
from pathlib import Path
import struct


def validate(directory,width,height,frames):
    files=sorted(directory.glob('*.png'))
    if len(files)!=frames:
        raise ValueError(f'Expected {frames} PNG frames, found {len(files)}')
    for index,path in enumerate(files,1):
        if path.name!=f'{index:04d}.png':
            raise ValueError(f'Non-contiguous frame: {path}')
        data=path.read_bytes()
        if data[:8]!=b'\x89PNG\r\n\x1a\n' or data[12:16]!=b'IHDR':
            raise ValueError(f'Invalid PNG: {path}')
        actual_width,actual_height,depth,color=struct.unpack('>IIBB',data[16:26])
        if (actual_width,actual_height,depth,color)!=(width,height,8,6):
            raise ValueError(f'Expected {width}x{height} 8-bit RGBA: {path}')
    print(f'Validated {frames} Blender RGBA PNG frames at {width}x{height}')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('--resolution',default='1920x1080',choices=['1920x1080','1280x720','960x540'])
    parser.add_argument('--frames',type=int,default=30)
    args=parser.parse_args()
    width,height=map(int,args.resolution.split('x'))
    validate(args.directory,width,height,args.frames)
