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

    def test_schema1_normalizes_default_states(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sheet.png").write_bytes(b"x")
            manifest = root / "pose-sheet.json"
            manifest.write_text(json.dumps({
                "schema": 1,
                "actor_id": "paul-bear",
                "source": "sheet.png",
                "poses": [
                    {"id": "drive", "type": "seated_driver"},
                    {"id": "look", "type": "seated_driver"},
                    {"id": "lean", "type": "seated_driver"},
                    {"id": "phone", "type": "seated_driver"}
                ]
            }))
            schema, actor_id, pack_kind, _, poses = pose_sheet.load_manifest(manifest)
            self.assertEqual(schema, 1)
            self.assertEqual(actor_id, "paul-bear")
            self.assertEqual(pack_kind, "actor")
            self.assertEqual(
                poses[0],
                {"id": "drive", "type": "seated_driver", "gaze": "forward",
                 "mouth": "closed", "interaction": "none"}
            )

    def test_schema2_supports_gaze_mouth_and_interaction(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sheet.png").write_bytes(b"x")
            manifest = root / "pose-sheet.json"
            manifest.write_text(json.dumps({
                "schema": 2,
                "actor_id": "yvonne-bear",
                "pack_kind": "actor",
                "source": "sheet.png",
                "poses": [
                    {"id": "listen", "type": "seated_table", "gaze": "partner", "mouth": "smile", "interaction": "table"},
                    {"id": "sing", "type": "seated_table", "gaze": "partner", "mouth": "singing_open", "interaction": "table"},
                    {"id": "soft", "type": "seated_table", "gaze": "down", "mouth": "soft_open", "interaction": "table"},
                    {"id": "rest", "type": "seated_table", "gaze": "forward", "mouth": "closed", "interaction": "table"}
                ]
            }))
            schema, actor_id, pack_kind, _, poses = pose_sheet.load_manifest(manifest)
            self.assertEqual(schema, 2)
            self.assertEqual(actor_id, "yvonne-bear")
            self.assertEqual(pack_kind, "actor")
            self.assertEqual(poses[1]["mouth"], "singing_open")
            self.assertEqual(poses[1]["gaze"], "partner")

    def test_interaction_pack_requires_interaction(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sheet.png").write_bytes(b"x")
            manifest = root / "pose-sheet.json"
            poses = [
                {"id": n, "type": "performance", "gaze": "audience", "mouth": "closed", "interaction": "none"}
                for n in ("a","b","c","d")
            ]
            manifest.write_text(json.dumps({
                "schema": 2, "actor_id": "paul-bear", "pack_kind": "interaction",
                "source": "sheet.png", "poses": poses
            }))
            with self.assertRaisesRegex(pose_sheet.ValidationError, "non-none interaction"):
                pose_sheet.load_manifest(manifest)

    def test_manifest_rejects_duplicate_pose_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sheet.png").write_bytes(b"x")
            manifest = root / "pose-sheet.json"
            manifest.write_text(json.dumps({
                "schema": 1,
                "actor_id": "bear",
                "source": "sheet.png",
                "poses": [
                    {"id": "same", "type": "standing"},
                    {"id": "same", "type": "standing"},
                    {"id": "three", "type": "standing"},
                    {"id": "four", "type": "standing"}
                ]
            }))
            with self.assertRaisesRegex(pose_sheet.ValidationError, "duplicate pose"):
                pose_sheet.load_manifest(manifest)

    def test_manifest_rejects_path_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "pose-sheet.json"
            manifest.write_text(json.dumps({
                "schema": 1,
                "actor_id": "bear",
                "source": "../sheet.png",
                "poses": [
                    {"id": "one", "type": "standing"},
                    {"id": "two", "type": "standing"},
                    {"id": "three", "type": "standing"},
                    {"id": "four", "type": "standing"}
                ]
            }))
            with self.assertRaisesRegex(pose_sheet.ValidationError, "stay inside"):
                pose_sheet.load_manifest(manifest)

    def test_manifest_rejects_unknown_mouth_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sheet.png").write_bytes(b"x")
            manifest = root / "pose-sheet.json"
            poses = [
                {"id": n, "type": "standing", "gaze": "forward", "mouth": "yodel", "interaction": "none"}
                for n in ("a","b","c","d")
            ]
            manifest.write_text(json.dumps({
                "schema": 2, "actor_id": "bear", "pack_kind": "actor",
                "source": "sheet.png", "poses": poses
            }))
            with self.assertRaisesRegex(pose_sheet.ValidationError, "mouth must be one of"):
                pose_sheet.load_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
