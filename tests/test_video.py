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

    def test_concat_stream_copy_combines_duration_and_strips_audio(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            clip1 = root / "clip 'one' space.mp4"
            clip2 = root / "clip two.mp4"
            out = root / "review result.mp4"
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=black:s=160x90:r=30:d=1','-f','lavfi','-i','sine=frequency=440:duration=1','-c:v','libx264','-c:a','aac','-pix_fmt','yuv420p',str(clip1)],check=True)
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=white:s=160x90:r=30:d=1','-f','lavfi','-i','sine=frequency=880:duration=1','-c:v','libx264','-c:a','aac','-pix_fmt','yuv420p',str(clip2)],check=True)
            clip1_bytes = clip1.read_bytes()
            clip2_bytes = clip2.read_bytes()

            subprocess.run(['python3','scripts/video.py','concat',str(clip1),str(clip2),str(out)],check=True)
            video.validate(out, 160, 90, 30, 2)
            streams = video.probe(out)['streams']
            self.assertEqual(len([s for s in streams if s['codec_type'] == 'video']), 1)
            self.assertEqual(streams[0]['codec_name'], 'h264')
            self.assertFalse(any(s['codec_type'] == 'audio' for s in streams))
            self.assertEqual(clip1.read_bytes(), clip1_bytes)
            self.assertEqual(clip2.read_bytes(), clip2_bytes)

    def test_concat_rejects_incompatible_dimensions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            clip1 = root / 'clip1.mp4'
            clip2 = root / 'clip2.mp4'
            out = root / 'out.mp4'
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=black:s=160x90:r=30:d=1','-c:v','libx264','-pix_fmt','yuv420p',str(clip1)],check=True)
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=black:s=320x180:r=30:d=1','-c:v','libx264','-pix_fmt','yuv420p',str(clip2)],check=True)

            with self.assertRaises(ValueError):
                video.concat([clip1, clip2], out)
            self.assertFalse(out.exists())

            proc = subprocess.run(['python3','scripts/video.py','concat',str(clip1),str(clip2),str(out)], capture_output=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertFalse(out.exists())

    def test_concat_rejects_aliasing_and_insufficient_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            clip1 = root / 'clip1.mp4'
            clip2 = root / 'clip2.mp4'
            out = root / 'out.mp4'
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=black:s=160x90:r=30:d=1','-c:v','libx264','-pix_fmt','yuv420p',str(clip1)],check=True)
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=black:s=160x90:r=30:d=1','-c:v','libx264','-pix_fmt','yuv420p',str(clip2)],check=True)
            clip1_bytes = clip1.read_bytes()

            with self.assertRaises(ValueError):
                video.concat([clip1, clip2], clip1)
            self.assertEqual(clip1.read_bytes(), clip1_bytes)

            with self.assertRaises(ValueError):
                video.concat([clip1], out)
            self.assertFalse(out.exists())

    def test_concat_rejects_different_stream_time_bases(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, second, output = root/'first.mp4', root/'second.mp4', root/'output.mp4'
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=black:s=160x90:r=30:d=1','-c:v','libx264','-pix_fmt','yuv420p',str(first)],check=True)
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(first),'-c:v','copy','-video_track_timescale','90000',str(second)],check=True)
            output.write_bytes(b'previous review')
            with self.assertRaisesRegex(ValueError, 'time base'):
                video.concat([first, second], output)
            self.assertEqual(output.read_bytes(), b'previous review')
