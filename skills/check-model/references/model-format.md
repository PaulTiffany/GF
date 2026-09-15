# Model format, schema 1

A model contains exactly `schema`, `variables`, `initial`, `transitions`, and
`invariants`. See [stale-review.json](../examples/stale-review.json) for a complete
input. This is a deliberately small JSON language; no expressions are Python.

- `variables`: 1-12 named finite domains, each with 1-32 distinct values of one
  type: boolean, integer, or string. Booleans and integers are different types.
- `initial`: one value for every variable, inside its declared domain.
- `transitions`: up to 64 objects with unique `id`, boolean `when`, and a `set`
  map of assignments. An empty transition list is allowed.
- `invariants`: 1-16 named boolean expressions that must hold in every reachable
  state, including the initial state.

Names start with a lowercase letter and use lowercase letters, digits,
underscores, or hyphens, with at most 64 characters. Strings have at most 64
characters. Integer literals have absolute value at most 1,000,000. Floats,
nulls, duplicate JSON keys, unknown fields, and unknown operators are rejected.

## Expressions

Literals are scalar values. Every operator expression is an object with one key.

| Expression | Result / requirement |
| --- | --- |
| `{"var": "revision"}` | Current value of a declared variable. |
| `{"not": EXPR}` | Boolean negation. |
| `{"and": [EXPR, ...]}` / `{"or": [EXPR, ...]}` | 1-8 boolean operands. |
| `{"eq": [A, B]}` / `{"ne": [A, B]}` | Equality / inequality of matching types. |
| `{"lt": [A, B]}` / `{"le": [A, B]}` | Integer ordering. |
| `{"add": [A, B]}` / `{"sub": [A, B]}` | Integer addition / subtraction. |

Operator nesting is capped at 12. Guards and invariants must have boolean type;
assignment expression types must match their target domains. Values produced
by an enabled transition must remain in those domains. A reachable out-of-domain
assignment is a model error, never a silently disabled transition.

## Execution semantics

The system starts at the single initial state. At each step, any transition with
a true guard may run. Every assigned value is computed from the old state, then
all assignments take effect together. Unassigned variables retain their values.
No fairness assumptions or external events are implicit.

Breadth-first search stores exact state tuples and explores each new state once.
The first invariant failure gives a shortest transition sequence from the initial
state; ties follow transition order. Budget exhaustion means `inconclusive`.
Only exhaustion of the reachable state graph yields `holds`.

Reports include a SHA-256 of canonical JSON model content (sorted object keys,
compact separators, ASCII escaping). Whitespace changes do not change that
digest. Changes to state domains, guards, updates, or invariants do. Replay
checks concrete witness legality; it does not attest to search statistics or
shortestness supplied by someone else.

For background on modeling concurrent systems, invariants, and atomic steps,
see the [SPIN manual](https://spinroot.com/spin/Man/Manual.html). GF uses its own
small explicit-state interpreter; SPIN is not a dependency or compatibility target.
