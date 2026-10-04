import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "skills" / "make-music-video" / "scripts" / "scene_contract.py"
spec = importlib.util.spec_from_file_location("scene_contract", MODULE)
scene_contract = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(scene_contract)


class SceneContractTests(unittest.TestCase):
    def scene(self):
        return {
            "schema": 1,
            "id": "car",
            "character_free": True,
            "required_assets": [
                {"id": "car_back", "role": "set", "z": 20},
                {"id": "dash", "role": "occluder", "z": 40}
            ],
            "optional_assets": [],
            "actor_slots": [{
                "id": "driver",
                "accepts": ["seated_driver"],
                "anchor": {"x": 0.4, "y": 0.6},
                "scale": 0.3,
                "facing": "front",
                "z": 30,
                "occluded_by": ["dash"]
            }],
            "motion_defaults": {"actors": "hold_pose"}
        }

    def actor(self, pose_type="seated_driver"):
        return {
            "schema": 1,
            "actor_id": "paul-bear",
            "source": "paul.png",
            "poses": [
                {"id": "a", "type": pose_type},
                {"id": "b", "type": pose_type},
                {"id": "c", "type": pose_type},
                {"id": "d", "type": pose_type}
            ]
        }

    def write(self, root, name, value):
        p = root / name
        p.write_text(json.dumps(value))
        return p

    def test_matches_compatible_pose_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scene = scene_contract.load_scene(self.write(root, "scene.json", self.scene()))
            actor = scene_contract.load_actor_sheet(self.write(root, "actor.json", self.actor()))
            result = scene_contract.compatible(scene, actor, "driver")
            self.assertTrue(result["compatible"])
            self.assertEqual(len(result["compatible_poses"]), 4)

    def test_rejects_incompatible_pose_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scene = scene_contract.load_scene(self.write(root, "scene.json", self.scene()))
            actor = scene_contract.load_actor_sheet(self.write(root, "actor.json", self.actor("standing")))
            result = scene_contract.compatible(scene, actor, "driver")
            self.assertFalse(result["compatible"])
            self.assertEqual(result["compatible_poses"], [])

    def test_scene_must_be_character_free(self):
        value = self.scene()
        value["character_free"] = False
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(scene_contract.ValidationError, "character_free"):
                scene_contract.load_scene(self.write(root, "scene.json", value))

    def test_occluder_reference_must_exist(self):
        value = self.scene()
        value["actor_slots"][0]["occluded_by"] = ["missing"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(scene_contract.ValidationError, "unknown occluder"):
                scene_contract.load_scene(self.write(root, "scene.json", value))


if __name__ == "__main__":
    unittest.main()
