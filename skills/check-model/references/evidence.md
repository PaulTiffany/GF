# Exemplar: stale review

This synthetic model asks whether an item can be merged after its reviewed
revision has changed. It is an illustration, not an audit of GF, GitHub,
Tiffany's readback Action, or anyone's live repository.

The model has two revisions, three possible reviewed values (including an
unreviewed marker), a merged flag, and three actions: review, edit, and merge.
Its invariant requires a merged item to have its current revision reviewed.

Observed locally on 2026-09-15 with the bundled helper:

| Input | Result |
| --- | --- |
| `examples/stale-review.json` | Counterexample: review revision 0, edit to revision 1, merge using the old review. Three transitions; witness replay accepted. |
| `examples/revision-bound-review.json` | The merge guard requires the reviewed revision to equal the current revision. All 7 reachable states exhausted; invariant holds in this model. |

The examples differ only in the merge guard. The real implementation must make
that guard and merge one atomic operation for this abstraction to apply. The
result does not establish liveness, coverage of further revisions, or behavior
of external software.

Repository tests exercise witness legality and tampering, initial-state
violations, closed cycles, simultaneous assignment, type/domain errors, and
budget exhaustion. Generated finite graphs are also checked against an
independent shortest-path calculation. These are implementation checks, not a
machine-checked proof of the checker itself.
