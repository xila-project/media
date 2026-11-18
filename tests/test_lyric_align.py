"""Exercise the lyric alignment CLI against timed Scribe fixtures."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LyricAlignTests(unittest.TestCase):
    def align(self, lyrics, words, duration=20):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SONG.md").write_text("## Lyrics\n" + lyrics)
            (root / "scribe.json").write_text(json.dumps({
                "words": [
                    {"text": text, "start": start, "end": end}
                    for text, start, end in words
                ]
            }))
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/lyric_align.py"),
                 "--lyrics", "SONG.md", "--words", "scribe.json",
                 "--bpm", "128", "--duration", str(duration), "--out", "cues.json"],
                cwd=root, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads((root / "cues.json").read_text()), result.stdout

    def test_annotated_headers_and_repeat_counts_expand_lines(self):
        cues, _ = self.align(
            "**[Drop]** _(hook only)_\nBOTH: Not your regular! ×2\n",
            [("Not", 1.0, 1.2), ("your", 1.2, 1.4), ("regular", 1.4, 2.0),
             ("Not", 3.0, 3.2), ("your", 3.2, 3.4), ("regular", 3.4, 4.0)],
        )
        self.assertEqual([section["name"] for section in cues["sections"]], ["Drop"])
        self.assertEqual(len(cues["lines"]), 2)
        self.assertNotIn("×", json.dumps(cues["lines"], ensure_ascii=False))

    def test_compounds_numbers_and_scribe_spelling_errors_keep_measured_times(self):
        cues, _ = self.align(
            "**[Verse]**\nXILA: Two-fifty-six kibibytes of RAM!\n"
            "XILA: Xila dot dev.\n## Notes\nALIX: Ignore me.",
            [("256", 1, 1.5), ("kibi", 1.6, 1.9), ("bytes", 2, 2.3),
             ("of", 2.3, 2.4), ("RAM.", 2.4, 2.8), ("Xyla.dev,", 3, 3.9)],
        )
        first, second = cues["lines"]
        self.assertEqual(first["speaker"], "XILA")
        self.assertEqual(first["at"], "1.3e")
        self.assertEqual([(word["start"], word["end"]) for word in first["words"]],
                         [(1, 1.5), (1.6, 2.3), (2.3, 2.4), (2.4, 2.8)])
        self.assertEqual([word["start"] for word in second["words"]], [3, 3.3, 3.6])
        self.assertEqual((cues["sections"][0]["start"], cues["sections"][0]["end"]), (1, 3.9))

    def test_repeated_hooks_do_not_reuse_transcript_or_steal_next_line(self):
        cues, report = self.align(
            "**[Chorus]**\nBOTH: Not your regular! (O-S!)\n"
            "XILA: OS on a board.\nBOTH: Not your regular! (O-S!)\n"
            "**[Chorus]**\nBOTH: Not your regular! (O-S!)\n"
            "ALIX: Goodbye.\n",
            [("Not", 1, 1.2), ("your", 1.2, 1.4), ("regular", 1.4, 1.9),
             ("OS", 2.2, 2.4), ("on", 2.4, 2.5), ("a", 2.5, 2.6), ("board", 2.6, 3),
             ("Not", 4, 4.2), ("your", 4.2, 4.4), ("regular", 4.4, 4.8),
             ("O", 5, 5.1), ("S", 5.1, 5.4), ("Goodbye", 6, 6.4)],
        )
        first, reply, hook, missing, _ = cues["lines"]
        self.assertEqual(first["end"], 1.9)
        self.assertTrue(first["words"][-1]["interpolated"])
        self.assertFalse(first.get("low_confidence", False))
        self.assertEqual(reply["start"], 2.2)
        self.assertTrue(missing["missing"])
        self.assertNotIn("start", missing)
        self.assertEqual((hook["start"], hook["end"]), (4, 5.4))
        self.assertNotEqual(cues["sections"][0]["id"], cues["sections"][1]["id"])
        self.assertIn("1/2", report)
        self.assertIn("Missing lines", report)

    def test_weak_partial_match_interpolates_between_anchors(self):
        cues, report = self.align(
            "**[Bridge]**\nALIX: Order right now!\n"
            "XILA: (Open a tab.)\nALIX: Operators are standing by.",
            [("Order", 1, 1.25), ("eh", 1.3, 1.5), ("now", 1.75, 2),
             ("Open", 3, 3.4), ("a", 3.5, 3.6), ("tab", 3.7, 4)],
        )
        partial, ad_lib, missing = cues["lines"]
        self.assertTrue(partial["low_confidence"])
        self.assertEqual(partial["words"][1], {
            "text": "right", "start": 1.25, "end": 1.75,
            "at": "1.3a", "endAt": "1.4a", "interpolated": True,
        })
        self.assertEqual(ad_lib["start"], 3)
        self.assertTrue(missing["missing"])
        self.assertEqual(cues["sections"][0]["end"], 4)
        self.assertIn("Low-confidence lines", report)

    def test_an_entirely_missing_section_has_no_inferred_boundary(self):
        cues, _ = self.align(
            "**[Intro]**\nALIX: Giant forklift.\n"
            "**[Outro]**\nXILA: Goodbye.\n",
            [("Goodbye", 10, 10.4)],
        )
        self.assertTrue(cues["sections"][0]["missing"])
        self.assertNotIn("startBar", cues["sections"][0])
        self.assertEqual(cues["sections"][1]["start"], 10)
        self.assertEqual(cues["duration"], 20)
