import copy
import importlib.util
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "skills/check-model"
SCRIPT = PACKAGE / "scripts/check_model.py"
spec = importlib.util.spec_from_file_location("check_model", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def example(name):
    return json.loads((PACKAGE / "examples" / f"{name}.json").read_text())


def counter_model():
    return {"schema": 1, "variables": {"n": [0, 1, 2]}, "initial": {"n": 0},
            "transitions": [{"id": "increment", "when": {"lt": [{"var": "n"}, 2]},
                             "set": {"n": {"add": [{"var": "n"}, 1]}}}],
            "invariants": {"bounded": {"le": [{"var": "n"}, 2]}}}


class ModelCheckTests(unittest.TestCase):
    def test_stale_review_has_a_shortest_replayable_witness(self):
        model = checker.Model(example("stale-review"))
        result = checker.search(model)
        self.assertEqual(result["status"], "counterexample")
        self.assertEqual([step["via"] for step in result["trace"]], [None, "review", "edit", "merge"])
        self.assertEqual(checker.replay(model, result)["steps"], 3)

    def test_revision_guard_exhausts_the_reachable_states(self):
        result = checker.search(checker.Model(example("revision-bound-review")))
        self.assertEqual(result["status"], "holds")
        self.assertTrue(result["complete"])
        self.assertEqual(result["stats"]["states_visited"], 7)

    def test_initial_violation_is_a_zero_step_witness(self):
        data = counter_model()
        data["invariants"] = {"false-at-start": False}
        model = checker.Model(data)
        result = checker.search(model)
        self.assertEqual(checker.replay(model, result)["steps"], 0)

    def test_cycles_and_terminal_states_can_finish_at_exact_budgets(self):
        data = counter_model()
        data["transitions"] = [{"id": "loop", "when": True, "set": {}}]
        result = checker.search(checker.Model(data), max_states=1, max_checks=1, max_depth=0)
        self.assertEqual(result["status"], "holds")
        data["transitions"] = []
        self.assertEqual(checker.search(checker.Model(data), max_depth=0)["status"], "holds")
        self.assertEqual(checker.search(checker.Model(counter_model()), max_depth=2)["status"], "holds")

    def test_assignments_are_simultaneous(self):
        data = {"schema": 1, "variables": {"x": [1, 2], "y": [1, 2]},
                "initial": {"x": 1, "y": 2},
                "transitions": [{"id": "swap", "when": True,
                                 "set": {"x": {"var": "y"}, "y": {"var": "x"}}}],
                "invariants": {"different": {"ne": [{"var": "x"}, {"var": "y"}]}}}
        result = checker.search(checker.Model(data))
        self.assertEqual(result["status"], "holds")
        self.assertEqual(result["stats"]["states_visited"], 2)

    def test_reachable_domain_escape_is_an_error(self):
        data = counter_model()
        data["transitions"][0]["when"] = True
        with self.assertRaisesRegex(ValueError, "outside declared domain"):
            checker.search(checker.Model(data))

    def test_each_budget_yields_inconclusive(self):
        model = checker.Model(example("stale-review"))
        cases = [({"max_states": 1}, "state limit"), ({"max_checks": 1}, "transition-check limit"),
                 ({"max_depth": 0}, "depth limit"),
                 ({"seconds": 0.1, "clock": itertools.count().__next__}, "time limit")]
        for kwargs, reason in cases:
            with self.subTest(reason=reason):
                result = checker.search(model, **kwargs)
                self.assertEqual(result["status"], "inconclusive")
                self.assertFalse(result["complete"])
                self.assertEqual(result["reason"], reason)

    def test_replay_rejects_changed_or_incomplete_evidence(self):
        model = checker.Model(example("stale-review"))
        original = checker.search(model)
        variants = []
        report = copy.deepcopy(original)
        report["trace"][1]["state"]["reviewed"] = 1
        variants.append(report)
        report = copy.deepcopy(original)
        report["trace"][1]["via"] = "merge"
        variants.append(report)
        report = copy.deepcopy(original)
        report["trace"].pop()
        variants.append(report)
        variants.extend([{**original, "model_sha256": "0" * 64}, {**original, "schema": True}])
        for report in variants:
            with self.assertRaises(ValueError):
                checker.replay(model, report)

    def test_types_operators_and_duplicate_keys_are_rejected(self):
        data = counter_model()
        data["variables"]["n"] = [0, True]
        with self.assertRaises(ValueError):
            checker.Model(data)
        data = counter_model()
        data["transitions"][0]["when"] = {"python": "print('unexpected execution')"}
        with self.assertRaisesRegex(ValueError, "Unknown operator"):
            checker.Model(data)
        data = counter_model()
        data["invariants"] = {"typed": {"eq": [{"var": "n"}, True]}}
        with self.assertRaisesRegex(ValueError, "matching types"):
            checker.Model(data)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "duplicate.json"
            path.write_text('{"schema":1,"schema":2}')
            with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
                checker.read_json(path, checker.MAX_MODEL_BYTES)

    def test_generated_graphs_agree_with_independent_shortest_paths(self):
        rng = random.Random(27)
        for size in range(1, 7):
            for _ in range(6):
                edges = [(a, b) for a in range(size) for b in range(size) if rng.random() < 0.28]
                # Bellman-Ford relaxation on the explicit graph, independent of the checker.
                distance = [float("inf")] * size
                distance[0] = 0
                for _ in range(size - 1):
                    old = distance[:]
                    for a, b in edges:
                        distance[b] = min(distance[b], old[a] + 1)
                data = {"schema": 1, "variables": {"q": list(range(size))}, "initial": {"q": 0},
                        "transitions": [{"id": f"edge-{a}-{b}", "when": {"eq": [{"var": "q"}, a]},
                                         "set": {"q": b}} for a, b in edges],
                        "invariants": {"avoid-target": {"ne": [{"var": "q"}, size - 1]}}}
                model = checker.Model(data)
                result = checker.search(model)
                if distance[-1] < float("inf"):
                    self.assertEqual(result["status"], "counterexample")
                    self.assertEqual(checker.replay(model, result)["steps"], distance[-1])
                else:
                    self.assertEqual(result["status"], "holds")
                    self.assertEqual(result["stats"]["states_visited"], sum(d < float("inf") for d in distance))

    def test_invalid_or_excessive_budgets_are_rejected(self):
        model = checker.Model(counter_model())
        for kwargs in [{"max_states": 50_001}, {"max_depth": 129}, {"max_checks": True},
                       {"seconds": float("nan")}, {"seconds": 11}]:
            with self.assertRaises(ValueError):
                checker.search(model, **kwargs)

    def test_cli_verdicts_and_output_preservation(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "witness.json"
            model = PACKAGE / "examples/stale-review.json"
            command = [sys.executable, str(SCRIPT), "check", str(model), "--output", str(output)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 2, result.stderr)
            original = output.read_bytes()
            result = subprocess.run(command, capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(output.read_bytes(), original)
            result = subprocess.run([sys.executable, str(SCRIPT), "replay", str(model), str(output)],
                                    capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run(command[:-2] + ["--max-states", "1"],
                                    capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 3, result.stderr)


if __name__ == "__main__":
    unittest.main()
