"""Exercise screenshot replacement through the contributor-facing CLI."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]


def png(width, height):
    def chunk(kind, data):
        return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data))
    header = struct.pack('!2I5B', width, height, 8, 2, 0, 0, 0)
    pixels = (b'\0' + b'\xff\xff\xff' * width) * height
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + chunk(b'IDAT', zlib.compress(pixels)) + chunk(b'IEND', b'')


class ScreensTest(unittest.TestCase):
    def test_replace_preserves_layout_and_previous_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            production = root / 'productions/trailer/production.json'
            production.parent.mkdir(parents=True)
            layout = {'asset': None, 'width': 1280, 'height': 720, 'position': [0, 30]}
            production.write_text(json.dumps({'screens': {'main': layout}}))
            (root / 'assets').mkdir()
            (root / 'assets/catalog.json').write_text('{"assets": []}')
            source = root / 'capture.png'
            def run():
                return subprocess.run(['python3', str(ROOT / 'scripts/screens.py'), 'import', str(source),
                                       '--root', str(root), '--production', 'trailer', '--slot', 'main',
                                       '--origin', 'https://platforms.xila.dev/', '--author', 'Xila contributors',
                                       '--license', 'Apache-2.0'], capture_output=True, text=True)
            source.write_bytes(png(16, 9))
            first = run()
            self.assertEqual(first.returncode, 0, first.stderr)
            previous = json.loads(production.read_text())['screens']['main']['asset']
            self.assertEqual(run().returncode, 0)
            self.assertEqual(len(json.loads((root / 'assets/catalog.json').read_text())['assets']), 1)
            source.write_bytes(png(32, 18))
            result = run()
            self.assertEqual(result.returncode, 0, result.stderr)
            slot = json.loads(production.read_text())['screens']['main']
            self.assertNotEqual(slot.pop('asset'), previous)
            self.assertEqual(slot, {key: value for key, value in layout.items() if key != 'asset'})
            assets = json.loads((root / 'assets/catalog.json').read_text())['assets']
            self.assertEqual(len(assets), 2)
            for asset in assets:
                self.assertEqual(hashlib.sha256((root / asset['file']).read_bytes()).hexdigest(), asset['sha256'])
                self.assertGreater(asset['width'], 0)
            before = production.read_bytes()
            source.write_text('invalid image')
            self.assertNotEqual(run().returncode, 0)
            self.assertEqual(production.read_bytes(), before)
