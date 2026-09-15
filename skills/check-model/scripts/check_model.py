#!/usr/bin/env python3
"""Explore finite JSON models for invariant failures; replay concrete witnesses."""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
import math
from pathlib import Path
import re
import time

MAX_MODEL_BYTES = 131_072
MAX_REPORT_BYTES = 1_048_576
ID = re.compile(r"[a-z][a-z0-9_-]{0,63}")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def keys(value, expected, label):
    require(isinstance(value, dict) and set(value) == set(expected), f"Invalid fields in {label}")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path, limit):
    with Path(path).open("rb") as source:
        data = source.read(limit + 1)
    require(len(data) <= limit, "Input exceeds its byte limit")
    return json.loads(data, object_pairs_hook=unique_object)


def scalar_type(value):
    require(type(value) in (bool, int, str), "Values must be booleans, integers, or strings")
    require(type(value) is not int or abs(value) <= 1_000_000, "Integer literal exceeds limit")
    require(type(value) is not str or len(value) <= 64, "String literal exceeds limit")
    return type(value)


def expression_type(expr, kinds, depth=0):
    require(depth <= 12, "Expression nesting exceeds 12")
    if not isinstance(expr, dict):
        return scalar_type(expr)
    require(len(expr) == 1, "An expression must have exactly one operator")
    op, args = next(iter(expr.items()))
    if op == "var":
        require(isinstance(args, str) and args in kinds, "Unknown variable reference")
        return kinds[args]
    if op == "not":
        require(expression_type(args, kinds, depth + 1) is bool, "not needs a boolean")
        return bool
    require(op in {"and", "or", "eq", "ne", "lt", "le", "add", "sub"}, "Unknown operator")
    require(isinstance(args, list) and 1 <= len(args) <= 8, "Invalid operator arguments")
    types = [expression_type(arg, kinds, depth + 1) for arg in args]
    if op in {"and", "or"}:
        require(all(kind is bool for kind in types), "Boolean operator needs booleans")
        return bool
    require(len(types) == 2 and types[0] is types[1], "Binary operands need matching types")
    if op in {"eq", "ne"}:
        return bool
    require(types[0] is int, "Arithmetic and ordering need integers")
    return int if op in {"add", "sub"} else bool


def evaluate(expr, state):
    if not isinstance(expr, dict):
        return expr
    op, args = next(iter(expr.items()))
    if op == "var":
        return state[args]
    if op == "not":
        return not evaluate(args, state)
    values = [evaluate(arg, state) for arg in args]
    if op == "and":
        return all(values)
    if op == "or":
        return any(values)
    a, b = values
    if op == "eq":
        return a == b
    if op == "ne":
        return a != b
    if op == "lt":
        return a < b
    if op == "le":
        return a <= b
    return a + b if op == "add" else a - b


class Model:
    def __init__(self, data):
        keys(data, {"schema", "variables", "initial", "transitions", "invariants"}, "model")
        require(type(data["schema"]) is int and data["schema"] == 1, "Unsupported model schema")
        variables = data["variables"]
        require(isinstance(variables, dict) and 1 <= len(variables) <= 12, "Use 1 to 12 variables")
        self.names = sorted(variables)
        self.domains, self.kinds = {}, {}
        for name, domain in variables.items():
            require(ID.fullmatch(name) is not None, "Invalid variable name")
            require(isinstance(domain, list) and 1 <= len(domain) <= 32, "Use 1 to 32 domain values")
            kinds = [scalar_type(value) for value in domain]
            require(all(kind is kinds[0] for kind in kinds), "Domain values must have one type")
            require(len(set(domain)) == len(domain), "Duplicate domain value")
            self.domains[name], self.kinds[name] = set(domain), kinds[0]
        self.initial = self.state(data["initial"])
        self.transitions = data["transitions"]
        require(isinstance(self.transitions, list) and len(self.transitions) <= 64, "Use at most 64 transitions")
        seen = set()
        for transition in self.transitions:
            keys(transition, {"id", "when", "set"}, "transition")
            name = transition["id"]
            require(isinstance(name, str) and ID.fullmatch(name) is not None, "Invalid transition id")
            require(name not in seen, "Duplicate transition id")
            seen.add(name)
            require(expression_type(transition["when"], self.kinds) is bool, "Guard must be boolean")
            updates = transition["set"]
            require(isinstance(updates, dict) and set(updates) <= set(self.names), "Unknown assignment target")
            for target, expr in updates.items():
                require(expression_type(expr, self.kinds) is self.kinds[target], "Assignment type mismatch")
        invariants = data["invariants"]
        require(isinstance(invariants, dict) and 1 <= len(invariants) <= 16, "Use 1 to 16 invariants")
        self.invariants = dict(sorted(invariants.items()))
        for name, expr in self.invariants.items():
            require(ID.fullmatch(name) is not None, "Invalid invariant id")
            require(expression_type(expr, self.kinds) is bool, "Invariant must be boolean")
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        self.sha256 = hashlib.sha256(canonical.encode()).hexdigest()

    def state(self, values):
        keys(values, self.names, "state")
        for name in self.names:
            require(type(values[name]) is self.kinds[name] and values[name] in self.domains[name],
                    f"State value outside declared domain: {name}")
        return tuple(values[name] for name in self.names)

    def values(self, state):
        return dict(zip(self.names, state))

    def step(self, state, transition):
        old = self.values(state)
        if not evaluate(transition["when"], old):
            return None
        # All right-hand sides observe the same old state (one atomic transition).
        updates = {name: evaluate(expr, old) for name, expr in transition["set"].items()}
        return self.state({**old, **updates})

    def violation(self, state):
        values = self.values(state)
        return next((name for name, expr in self.invariants.items() if not evaluate(expr, values)), None)


def search(model, *, max_states=20_000, max_checks=200_000, max_depth=64, seconds=5.0,
           clock=time.monotonic):
    for value, lower, upper, label in [(max_states, 1, 50_000, "states"),
                                       (max_checks, 1, 500_000, "checks"),
                                       (max_depth, 0, 128, "depth")]:
        require(type(value) is int and lower <= value <= upper, f"Invalid {label} budget")
    require(type(seconds) in (int, float) and math.isfinite(seconds) and 0 < seconds <= 10,
            "Time budget must be positive and at most 10 seconds")
    start = clock()
    queue = deque([model.initial])
    parents = {model.initial: (None, None, 0)}
    checks = expanded = 0
    depth_cut = False

    def finish(status, reason=None, state=None, invariant=None):
        result = {"schema": 1, "model_sha256": model.sha256, "status": status,
                  "complete": status == "holds", "reason": reason,
                  "limits": {"states": max_states, "transition_checks": max_checks,
                             "depth": max_depth, "seconds": seconds},
                  "stats": {"states_visited": len(parents), "states_expanded": expanded,
                            "transition_checks": checks, "elapsed_seconds": round(clock() - start, 6)}}
        if status == "counterexample":
            trace = []
            while state is not None:
                parent, via, _ = parents[state]
                trace.append({"via": via, "state": model.values(state)})
                state = parent
            result.update(invariant=invariant, trace=list(reversed(trace)))
        return result

    failed = model.violation(model.initial)
    if failed is not None:
        return finish("counterexample", "invariant violated", model.initial, failed)
    while queue:
        if clock() - start >= seconds:
            return finish("inconclusive", "time limit")
        current = queue.popleft()
        depth = parents[current][2]
        expanded += 1
        for transition in model.transitions:
            if clock() - start >= seconds:
                return finish("inconclusive", "time limit")
            if checks >= max_checks:
                return finish("inconclusive", "transition-check limit")
            checks += 1
            following = model.step(current, transition)
            if following is None or following in parents:
                continue
            if depth >= max_depth:
                depth_cut = True
                continue
            if len(parents) >= max_states:
                return finish("inconclusive", "state limit")
            parents[following] = (current, transition["id"], depth + 1)
            failed = model.violation(following)
            if failed is not None:
                return finish("counterexample", "invariant violated", following, failed)
            queue.append(following)
    return finish("inconclusive", "depth limit") if depth_cut else finish("holds", "reachable states exhausted")


def replay(model, report):
    require(isinstance(report, dict) and type(report.get("schema")) is int and
            report["schema"] == 1, "Invalid report schema")
    require(report.get("status") == "counterexample", "Replay needs a counterexample")
    require(report.get("model_sha256") == model.sha256, "Witness belongs to a different model")
    trace = report.get("trace")
    require(isinstance(trace, list) and 1 <= len(trace) <= 129, "Invalid trace length")
    for item in trace:
        keys(item, {"via", "state"}, "trace step")
    current = model.state(trace[0]["state"])
    require(current == model.initial and trace[0]["via"] is None, "Trace must start at the initial state")
    transitions = {item["id"]: item for item in model.transitions}
    for item in trace[1:]:
        via = item["via"]
        require(isinstance(via, str) and via in transitions, "Unknown trace transition")
        following = model.step(current, transitions[via])
        require(following is not None and following == model.state(item["state"]), "Illegal trace step")
        current = following
    invariant = report.get("invariant")
    require(isinstance(invariant, str) and invariant in model.invariants, "Unknown witness invariant")
    require(not evaluate(model.invariants[invariant], model.values(current)), "Trace does not violate the invariant")
    return {"valid": True, "model_sha256": model.sha256, "invariant": invariant, "steps": len(trace) - 1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check")
    check.add_argument("model", type=Path)
    check.add_argument("--output", type=Path)
    check.add_argument("--max-states", type=int, default=20_000)
    check.add_argument("--max-checks", type=int, default=200_000)
    check.add_argument("--max-depth", type=int, default=64)
    check.add_argument("--seconds", type=float, default=5.0)
    replay_parser = commands.add_parser("replay")
    replay_parser.add_argument("model", type=Path)
    replay_parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        model = Model(read_json(args.model, MAX_MODEL_BYTES))
        if args.command == "replay":
            result = replay(model, read_json(args.report, MAX_REPORT_BYTES))
            code = 0
        else:
            if args.output is not None:
                require(not args.output.exists(), "Output exists; choose a new path")
            result = search(model, max_states=args.max_states, max_checks=args.max_checks,
                            max_depth=args.max_depth, seconds=args.seconds)
            code = {"holds": 0, "counterexample": 2, "inconclusive": 3}[result["status"]]
        payload = json.dumps(result, indent=2) + "\n"
        require(len(payload.encode()) <= MAX_REPORT_BYTES, "Report exceeds byte limit")
        if args.command == "check" and args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x", encoding="utf-8") as target:
                target.write(payload)
        print(payload, end="")
    except (OSError, ValueError, RecursionError) as error:
        parser.exit(1, f"check_model: {error}\n")
    raise SystemExit(code)


if __name__ == "__main__":
    main()
