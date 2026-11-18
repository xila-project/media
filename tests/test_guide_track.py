"""Exercise the guide CLI, exact grid, and delivered PCM stems."""

from array import array
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/house-guide-cues.json"


class GuideTrackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(directory.cleanup)
        cls.root = Path(directory.name)
        cls.cues = cls.root / "cues.json"
        cue_sheet = json.loads(FIXTURE.read_text())
        cue_sheet.update(
            bars=3,
            duration=5.806,
            sections=[dict(cue_sheet["sections"][0], bars=3)],
            lines=cue_sheet["lines"][:2],
            events=[
                dict(cue_sheet["events"][0], at="2.4"),
                *({"kind": "syllable", "at": at} for at in ("3.2", "3.2&", "3.3", "3.3&")),
            ],
        )
        cue_sheet["lines"][1]["words"][-1]["at"] = "2.4a"
        cue_sheet["lines"].append({
            "at": "3.2",
            "speaker": "XILA",
            "delivery": "vocoder",
            "text": "Two-fifty-six.",
            "words": [{"text": "Two-fifty-six", "at": "3.2", "pitch": 0}],
        })
        cls.cues.write_text(json.dumps(cue_sheet))
        result = cls.render(cls.root)
        if result.returncode:
            raise AssertionError(result.stderr)
        cls.samples = {}
        cls.params = {}
        for name in ("guide", "guide-music", "guide-vocals"):
            with wave.open(str(cls.root / f"{name}.wav"), "rb") as wav:
                cls.params[name] = wav.getparams()[:4]
                samples = array("h", wav.readframes(wav.getnframes()))
                if sys.byteorder != "little":
                    samples.byteswap()
                cls.samples[name] = samples

    @classmethod
    def render(cls, output):
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts/guide_track.py"), str(cls.cues), "--output", str(output)],
            capture_output=True,
            text=True,
        )

    def test_all_outputs_have_exact_declared_duration(self):
        for name, params in self.params.items():
            with self.subTest(name=name):
                self.assertEqual(params, (2, 2, 48000, 278688))

    def test_one_beat_mute_leaves_vocal_and_restarts_on_grid(self):
        # Beat 2.4 is 162581 samples in, and 3.1 is 185806 samples in.
        start, stop = 162581 * 2, 185806 * 2
        music = self.samples["guide-music"]
        vocals = self.samples["guide-vocals"]
        mix = self.samples["guide"]
        self.assertTrue(any(music[start - 2048 : start]))
        self.assertFalse(any(music[start:stop]))
        self.assertTrue(any(music[stop : stop + 128]))
        self.assertTrue(any(vocals[start:stop]))
        self.assertFalse(any(vocals[stop - 2 : stop + 512]))
        self.assertEqual(mix[start:stop], vocals[start:stop])
        self.assertTrue(all(m + v == total for m, v, total in zip(music, vocals, mix)))

    def test_spoken_subdivisions_leave_their_own_onsets(self):
        # "we", "book", and "the" use e, &, and a on 1.2.
        vocals = self.samples["guide-vocals"]
        self.assertFalse(any(vocals[: 23226 * 2]))
        for frame in (23226, 29032, 34839, 40645):
            self.assertFalse(any(vocals[frame * 2 - 2 : frame * 2 + 2]))
            self.assertTrue(any(vocals[frame * 2 : frame * 2 + 512]))

    def test_syllable_markers_retrigger_a_single_word(self):
        vocals = self.samples["guide-vocals"]
        for frame in (209032, 220645, 232258, 243871):
            with self.subTest(frame=frame):
                self.assertFalse(any(vocals[frame * 2 - 2 : frame * 2 + 2]))
                self.assertTrue(any(vocals[frame * 2 : frame * 2 + 512]))

    def test_rerender_is_byte_identical(self):
        rerender = self.root / "repeat"
        result = self.render(rerender)
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in self.samples:
            with self.subTest(name=name):
                self.assertEqual(
                    (rerender / f"{name}.wav").read_bytes(),
                    (self.root / f"{name}.wav").read_bytes(),
                )


if __name__ == "__main__":
    unittest.main()
