import importlib.util
import tempfile
import unittest
from pathlib import Path
spec = importlib.util.spec_from_file_location("brand", "scripts/brand.py")
brand = importlib.util.module_from_spec(spec)
spec.loader.exec_module(brand)
class BrandTests(unittest.TestCase):
    def test_corrupt_cache_is_rejected(self):
        with self.assertRaises(ValueError):
            brand.verify(b"corrupt", "0" * 64, "mark.svg")
    def test_local_checkout_is_pinned(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                brand.sync(Path(directory), Path(directory) / "cache")
