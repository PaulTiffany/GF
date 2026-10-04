import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "skills" / "make-music-video" / "scripts" / "lyric_overlay.py"
spec = importlib.util.spec_from_file_location("lyric_overlay", MODULE)
lyric_overlay = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(lyric_overlay)


class LyricOverlayTests(unittest.TestCase):
    def manifest(self):
        return {
            "schema": 1,
            "id": "demo",
            "duration": 8.0,
            "canvas": {"width": 1280, "height": 720, "fps": 30},
            "events": [{
                "start": 1.0,
                "end": 4.0,
                "text": "Sugar Bear",
                "behavior": "pulse",
                "anchor": {"x": 0.5, "y": 0.5},
                "scale": 1.0,
                "rotation_degrees": 0
            }]
        }

    def write(self, root, value):
        p = root / "overlay.json"
        p.write_text(json.dumps(value))
        return p

    def test_valid_manifest_compiles_manim_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            value = lyric_overlay.load_manifest(self.write(root, self.manifest()))
            source = lyric_overlay.compile_source(value)
            self.assertIn("class LyricOverlay(Scene)", source)
            self.assertIn('"behavior":"pulse"', source)

    def test_rejects_event_past_duration(self):
        value = self.manifest()
        value["events"][0]["end"] = 9.0
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(lyric_overlay.ValidationError, "between"):
                lyric_overlay.load_manifest(self.write(root, value))

    def test_rejects_unknown_behavior(self):
        value = self.manifest()
        value["events"][0]["behavior"] = "explode_everything"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(lyric_overlay.ValidationError, "must be one of"):
                lyric_overlay.load_manifest(self.write(root, value))

    def test_rejects_offscreen_anchor(self):
        value = self.manifest()
        value["events"][0]["anchor"]["x"] = 1.2
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(lyric_overlay.ValidationError, "between"):
                lyric_overlay.load_manifest(self.write(root, value))


if __name__ == "__main__":
    unittest.main()
