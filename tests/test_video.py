import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('video','scripts/video.py')
video=importlib.util.module_from_spec(spec)
spec.loader.exec_module(video)

class VideoTests(unittest.TestCase):
    def test_assembly_audio_padding_and_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            frames=root/'frames'; frames.mkdir()
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=black:s=320x180:r=30:d=1','-threads','1',str(frames/'%06d.png'),'-start_number','0'],check=True)
            # A shorter soundtrack must be padded to the video length.
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','sine=frequency=110:duration=0.2',str(root/'short.wav')],check=True)
            subprocess.run(['python3','scripts/video.py','assemble',str(frames),str(root/'video.mp4'),'--audio',str(root/'short.wav'),'--preset','fast'],check=True)
            video.validate(root/'video.mp4',320,180,30,1)
            streams=video.probe(root/'video.mp4')['streams']
            self.assertTrue(any(s['codec_type']=='audio' and s['sample_rate']=='48000' for s in streams))
            with self.assertRaises((AssertionError,ValueError)):
                video.validate(root/'video.mp4',1920,1080,30,1)

    def test_soundtrack_can_be_delayed_without_extending_video(self):
        import struct
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=black:s=160x90:r=30:d=1','-c:v','libx264','-pix_fmt','yuv420p',str(root/'silent.mp4')],check=True)
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','sine=frequency=220:duration=0.2',str(root/'cue.wav')],check=True)
            subprocess.run(['python3','scripts/video.py','soundtrack',str(root/'silent.mp4'),str(root/'cue.wav'),str(root/'result.mp4'),'--offset','0.5'],check=True)
            video.validate(root/'result.mp4',160,90,30,1)
            samples=subprocess.check_output(['ffmpeg','-v','error','-i',str(root/'result.mp4'),'-map','0:a:0','-f','s16le','-ac','1','-ar','48000','-'])
            values=struct.unpack('<'+'h'*(len(samples)//2),samples)
            self.assertLessEqual(max(map(abs,values[:12000])),1)
            self.assertGreater(max(map(abs,values[26400:28800])),100)
