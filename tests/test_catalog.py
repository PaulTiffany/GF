import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gf_catalog", ROOT / "catalog.py")
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / "skills/serve-gif"
        shutil.copytree(ROOT / "skills/serve-gif", self.package,
                        ignore=shutil.ignore_patterns("__pycache__"))
        self.index = {"schema": 1, "builds": [
            {"package": "skills/serve-gif", "checks": ["tests/check.py"]}
        ]}
        self.manifest = self.package / "build.json"
        self.build = json.loads(self.manifest.read_text())
        for check in self.index["builds"][0]["checks"]:
            path = self.root / check
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("raise AssertionError('Inspection must not execute checks')\n")
        self.save()

    def save(self):
        (self.root / "catalog.json").write_text(json.dumps(self.index))
        self.manifest.write_text(json.dumps(self.build))

    def test_inspects_the_contract_without_executing_helpers_or_checks(self):
        helper = self.package / self.build["entrypoint"]
        helper.write_text("raise AssertionError('Inspection must not execute helpers')\n")
        result = catalog.load_catalog(self.root)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "serve-gif")
        self.assertEqual(result[0]["effects"], ["local-read", "local-write"])
        self.assertEqual(result[0]["bounds"], self.build["bounds"])

    def test_rejects_missing_contract_fields_and_unknown_effects(self):
        self.build["effects"].append("unrestricted")
        self.save()
        with self.assertRaisesRegex(ValueError, "unknown effect"):
            catalog.load_catalog(self.root)
        self.build["effects"].pop()
        del self.build["bounds"]
        self.save()
        with self.assertRaisesRegex(ValueError, "expected fields"):
            catalog.load_catalog(self.root)

    def test_rejects_duplicate_build_ids(self):
        self.index["builds"].append(dict(self.index["builds"][0]))
        self.save()
        with self.assertRaisesRegex(ValueError, "Duplicate build id"):
            catalog.load_catalog(self.root)

    def test_references_cannot_leave_the_package(self):
        for name in ("../../catalog.json", str(self.root / "catalog.json")):
            with self.subTest(name=name):
                self.build["entrypoint"] = name
                self.save()
                with self.assertRaisesRegex(ValueError, "within its package"):
                    catalog.load_catalog(self.root)

    def test_symlinks_cannot_escape_the_package(self):
        link = self.package / "scripts/outside.py"
        link.symlink_to(self.root / self.index["builds"][0]["checks"][0])
        self.build["entrypoint"] = "scripts/outside.py"
        self.save()
        with self.assertRaisesRegex(ValueError, "escapes its package"):
            catalog.load_catalog(self.root)

    def test_missing_check_file_fails_validation(self):
        (self.root / self.index["builds"][0]["checks"][0]).unlink()
        with self.assertRaisesRegex(ValueError, "Missing reference"):
            catalog.load_catalog(self.root)

    def test_duplicate_json_keys_cannot_override_declared_effects(self):
        original = self.manifest.read_text()
        self.manifest.write_text(original[:-1] + ', "effects": []}')
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key: effects"):
            catalog.load_catalog(self.root)


if __name__ == "__main__":
    unittest.main()
