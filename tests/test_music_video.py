import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "skills" / "make-music-video" / "scripts" / "music_video.py"
spec = importlib.util.spec_from_file_location("music_video", MODULE)
music_video = importlib.util.module_from_spec(spec)
assert spec.loader is not None
import sys
sys.modules[spec.name] = music_video
spec.loader.exec_module(music_video)


class MusicVideoTests(unittest.TestCase):
    def project(self, root: Path, *, audio="media/song.wav", shots=None):
        media = root / "media"
        media.mkdir()
        for name in ("song.wav", "one.png", "two.mp4"):
            (media / name).write_bytes(b"x")
        value = {
            "schema": 1,
            "title": "Demo",
            "audio": audio,
            "width": 1280,
            "height": 720,
            "fps": 30,
            "shots": shots or [
                {"asset": "media/one.png", "kind": "image", "duration": 2.0},
                {"asset": "media/two.mp4", "kind": "video", "duration": 3.0, "source_start": 0.5},
            ],
        }
        path = root / "music-video.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_loads_bounded_project_and_builds_hard_cut_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = music_video.load_project(self.project(root))
            self.assertEqual(project.duration, 5.0)
            self.assertEqual(len(project.shots), 2)
            command = music_video.ffmpeg_argv(project, root / "out.mp4")
            joined = " ".join(command)
            self.assertIn("concat=n=2:v=1:a=0", joined)
            self.assertIn("scale=1280:720", joined)
            self.assertIn("-ss 0.5", joined)
            self.assertEqual(command[-1], str(root / "out.mp4"))

    def test_rejects_project_path_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.project(root, audio="../song.wav")
            with self.assertRaisesRegex(music_video.ValidationError, "stay inside"):
                music_video.load_project(path)

    def test_rejects_image_source_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.project(root, shots=[
                {"asset": "media/one.png", "kind": "image", "duration": 2.0, "source_start": 1.0}
            ])
            with self.assertRaisesRegex(music_video.ValidationError, "invalid or missing fields|only valid"):
                music_video.load_project(path)

    def test_rejects_excessive_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.project(root)
            value = json.loads(path.read_text())
            value["width"] = 3840
            value["height"] = 3840
            path.write_text(json.dumps(value))
            with self.assertRaisesRegex(music_video.ValidationError, "pixel bound"):
                music_video.load_project(path)


if __name__ == "__main__":
    unittest.main()
