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
