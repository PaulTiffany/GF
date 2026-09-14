import hashlib
import importlib.util
import io
import json
import re
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "prepare_gif", ROOT / "skills/serve-gif/scripts/prepare_gif.py")
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
render_spec = importlib.util.spec_from_file_location("gf", ROOT / "gf.py")
renderer = importlib.util.module_from_spec(render_spec)
render_spec.loader.exec_module(renderer)
GIF = ROOT / "out/lattice-animal.gif"


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / "delivered/dance.gif"

    def test_preserves_gif_bytes_and_reports_attachment(self):
        digest = hashlib.sha256(GIF.read_bytes()).hexdigest()
        result = helper.prepare(GIF, self.output, sha256=digest)
        self.assertEqual(self.output.read_bytes(), GIF.read_bytes())
        self.assertEqual(result["sha256"], digest)
        self.assertEqual((result["width"], result["height"], result["frames"]), (384, 384, 4))
        self.assertEqual(result["durations_ms"], [220] * 4)
        self.assertEqual(result["loop"], 0)
        self.assertEqual(result["markdown_image"], f"![Animated GIF](sandbox:{self.output})")
        self.assertEqual(helper.prepare(GIF, self.output), result)  # Safe retry.

    def test_zip_reads_only_the_selected_member_without_extracting_paths(self):
        archive = self.root / "artifact.zip"
        with ZipFile(archive, "w") as out:
            out.writestr("../outside.gif", GIF.read_bytes())
            out.writestr("unrelated.txt", b"unrelated")
        helper.prepare(archive, self.output, member="../outside.gif")
        self.assertEqual(self.output.read_bytes(), GIF.read_bytes())
        self.assertEqual(set(self.root.iterdir()), {archive, self.output.parent})
        with self.assertRaisesRegex(ValueError, "exactly one"):
            helper.prepare(archive, self.root / "missing.gif", member="not-there.gif")

    def test_wrong_hash_does_not_create_output(self):
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            helper.prepare(GIF, self.output, sha256="0" * 64)
        self.assertFalse(self.output.parent.exists())

    def test_static_and_non_gif_inputs_are_rejected(self):
        for name in ("still.gif", "still.png"):
            source = self.root / name
            Image.new("RGB", (8, 8), "red").save(source)
            with self.subTest(name=name), self.assertRaises(ValueError):
                helper.prepare(source, self.output)
        self.assertFalse(self.output.exists())

    def test_output_conflict_preserves_existing_files(self):
        player = self.root / "player.html"
        player.write_text("existing work")
        with self.assertRaisesRegex(ValueError, "different content"):
            helper.prepare(GIF, self.output, player=player)
        self.assertFalse(self.output.exists())
        self.assertEqual(player.read_text(), "existing work")

    def test_player_uses_composited_frames_and_escaped_alt(self):
        player = self.root / "player.html"
        alt = '\"><script>alert(1)</script> __ROOT__'
        helper.prepare(GIF, self.output, player=player, alt=alt)
        fragment = player.read_text()
        self.assertNotIn('<script>alert(1)</script>', fragment)
        self.assertIn('&lt;script&gt;', fragment)
        payload = json.loads(re.search(r'data-frames>(.*?)</script>', fragment, re.S)[1])
        self.assertEqual(payload["loop"], 0)
        self.assertEqual([frame["ms"] for frame in payload["frames"]], [220] * 4)
        import base64
        with Image.open(GIF) as original:
            for index, frame in enumerate(payload["frames"]):
                original.seek(index)
                with Image.open(io.BytesIO(base64.b64decode(frame["src"].split(",")[1]))) as png:
                    self.assertEqual(png.convert("RGBA").tobytes(), original.convert("RGBA").tobytes())

    def test_variable_timing_and_finite_loop_survive_preparation(self):
        source = self.root / "timing.gif"
        frames = [Image.new("RGB", (8, 8), color) for color in ("red", "green", "blue")]
        frames[0].save(source, save_all=True, append_images=frames[1:],
                       duration=[40, 100, 300], loop=1)
        result = helper.prepare(source, self.output)
        self.assertEqual(result["durations_ms"], [40, 100, 300])
        self.assertEqual(result["loop"], 1)

    def test_render_defaults_to_gif_and_poster(self):
        renderer.render(ROOT / "examples/lattice-animal.json", self.output)
        self.assertEqual({path.name for path in self.output.parent.iterdir()}, {"dance.gif", "dance.png"})
        with Image.open(self.output) as image:
            self.assertEqual(image.n_frames, 4)
        result = helper.prepare(self.output, self.output)
        self.assertEqual(result["durations_ms"], [220] * 4)


if __name__ == "__main__":
    unittest.main()
