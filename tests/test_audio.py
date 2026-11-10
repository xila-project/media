"""Exercise actual FFmpeg output, including silence rejection and embedded size."""
import json
import subprocess
import tempfile
import unittest
import wave
from pathlib import Path

class AudioTests(unittest.TestCase):
    def test_embedded_export(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['python3','scripts/audio.py','fixture',str(root/'test.wav')],check=True)
            subprocess.run(['python3','scripts/audio.py','process',str(root/'test.wav'),'--output',str(root/'result'),'--rate','22050'],check=True)
            with wave.open(str(root/'result/embedded.wav')) as audio:
                self.assertEqual(audio.getnchannels(),1)
                self.assertEqual(audio.getsampwidth(),2)
                self.assertEqual(audio.getframerate(),22050)
                self.assertEqual(audio.getnframes(),66150)
            self.assertLess((root/'result/embedded.wav').stat().st_size,134000)
            report=json.loads((root/'result/validation.json').read_text())
            self.assertLessEqual(report['peakDBFS'],-1.5)

    def test_silent_input_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with wave.open(str(root/'silence.wav'),'w') as audio:
                audio.setparams((1,2,22050,22050,'NONE','not compressed'))
                audio.writeframes(b'\0\0'*22050)
            result=subprocess.run(['python3','scripts/audio.py','process',str(root/'silence.wav'),'--output',str(root/'result')],capture_output=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn(b'silent',result.stderr.lower())
