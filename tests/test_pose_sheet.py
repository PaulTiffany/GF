import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "skills" / "make-music-video" / "scripts" / "pose_sheet.py"
spec = importlib.util.spec_from_file_location("pose_sheet", MODULE)
pose_sheet = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(pose_sheet)


class PoseSheetTests(unittest.TestCase):
    def test_crop_boxes_are_fixed_quadrants(self):
        self.assertEqual(
            pose_sheet.crop_boxes(800, 600),
            ((0, 0, 400, 300), (400, 0, 400, 300),
             (0, 300, 400, 300), (400, 300, 400, 300)),
        )

    def test_rejects_odd_dimensions(self):
        with self.assertRaisesRegex(pose_sheet.ValidationError, "even"):
            pose_sheet.crop_boxes(801, 600)

    def test_manifest_requires_exactly_four_unique_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sheet.png").write_bytes(b"x")
            manifest = root / "pose-sheet.json"
            manifest.write_text(json.dumps({
                "schema": 1,
                "source": "sheet.png",
                "poses": ["standing", "seated", "standing", "reclined"]
            }))
            with self.assertRaisesRegex(pose_sheet.ValidationError, "duplicate pose"):
                pose_sheet.load_manifest(manifest)

    def test_manifest_rejects_path_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "pose-sheet.json"
            manifest.write_text(json.dumps({
                "schema": 1,
                "source": "../sheet.png",
                "poses": ["standing", "seated", "left", "right"]
            }))
            with self.assertRaisesRegex(pose_sheet.ValidationError, "stay inside"):
                pose_sheet.load_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
