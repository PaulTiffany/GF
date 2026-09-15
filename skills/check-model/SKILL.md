---
name: check-model
description: Search finite workflow or protocol models for safety-invariant violations and replay concrete witnesses. Use for bounded counterexample searches, interleaving checks, or validating an explicit finite model. Does not verify arbitrary source code or liveness.
---

# Check a finite model

Use the bundled Python 3.10+ helper to explore reachable states rather than
relying on a plausible execution story. It needs only the standard library,
local inputs, and a writable output location when saving a report.

## Model the actual question

Read [references/model-format.md](references/model-format.md) when creating or
changing a model. Start with the supplied state domains, initial state,
transitions, and invariant. State any abstraction assumptions explicitly.

Each transition is atomic. Preserve separate steps that can interleave in the
system being modeled. Combining a read and write changes the model's guarantee.
Do not silently shrink domains, remove transitions, strengthen guards, or change
the invariant to obtain a passing result. Show a proposed fix as a separate model.

## Run and interpret

Resolve these script paths against the skill folder:

```bash
python scripts/check_model.py check examples/stale-review.json \
  --output /workspace/review-counterexample.json
python scripts/check_model.py replay examples/stale-review.json \
  /workspace/review-counterexample.json
```

| Check exit | Report status | Meaning |
| --- | --- | --- |
| 0 | `holds` | All reachable states of this finite model were exhausted without an invariant failure. |
| 2 | `counterexample` | A shortest failing transition sequence was found. Replay it. |
| 3 | `inconclusive` | A state, transition-check, depth, or time limit prevented completion. |
| 1 | Error on stderr | Invalid input or another tool error; no verification claim. |

Exit 2 is an expected finding. Read the JSON before deciding whether a run needs
repair. Replay has exit 0 for a valid witness and 1 for a rejected witness.

Defaults are 20,000 states, 200,000 transition checks, depth 64, and 5 seconds
of search. CLI flags can lower these budgets. Hard ceilings are 50,000 states,
500,000 checks, depth 128, and 10 seconds. The clock is checked between search
steps; this is not OS-level CPU isolation. Model input is capped at 128 KiB and
report input/output at 1 MiB. Existing output paths are preserved.

## Deliver evidence

For a counterexample, run `replay` against the same model and saved report.
It checks the model digest, initial state, enabled transitions, simultaneous
updates, and final invariant failure without repeating the search. It shares
the model semantics with the checker; it is not an independent proof kernel.

Show the short failing sequence and the state values that explain the failure.
For `holds`, state the modeled domains, assumptions, and explored-state count.
For `inconclusive`, report the limiting budget without calling the model safe.
Use the host's file persistence and presentation rules for saved deliverables.

Keep conclusions scoped to the model. This helper does not establish fairness,
eventual progress, deadlock freedom, real implementation behavior, or a theorem
about unbounded domains. See [references/evidence.md](references/evidence.md)
for the synthetic review example and validation record. Retain `LICENSE` when
copying the package.
