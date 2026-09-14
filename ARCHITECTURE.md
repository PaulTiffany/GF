# An executable build wiki

GF stores small capabilities that another equipped assistant can inspect,
reproduce, and improve. Each build couples a short lesson with executable code
and evidence. GitHub provides version history, distribution, CI, and reviewed
contributions. The host supplies the runtime and any authority to act.

## The pieces

| File | Responsibility |
| --- | --- |
| `catalog.json` | Index package locations and repository checks. |
| `catalog.py` | List builds, show their declarations, and validate metadata. |
| `skills/<id>/build.json` | Declare requirements, inputs, outputs, effects, bounds, and stopping conditions. |
| `skills/<id>/SKILL.md` | Teach the move and when to use it. |
| `skills/<id>/scripts/` and optional `assets/` | Perform the narrow task; keep fragile mechanics reusable. |
| Package evidence records | Describe what was tested or observed and what remains unknown. |
| Package `LICENSE` | Preserve the terms when the folder travels independently. |

Package references stay inside the package. Repository checks are indexed
separately so a copied build can operate without GF's test harness. Adding a
build does not require changing the catalogue program.

## Equip and execute

1. Choose a build with `python catalog.py list`.
2. Inspect it with `python catalog.py show serve-gif`, then read its skill and
   helper at the chosen revision. Share commit permalinks for reproducibility.
3. Match its requirements, effects, and bounds to the user's task and tools.
4. Run the helper with the requested inputs in the host's workspace.
5. Deliver the result through the host's supported surface and record the
   relevant observation. An improvement can come back through a reviewed PR.

The catalogue never imports helpers, executes declared checks, installs
packages, dispatches Actions, or acquires credentials. Inspection is read-only.
The assistant invokes a helper separately under the user's existing authority.

## Bounded fun

Concentrate the build on one useful result. Use small local fixtures for
experiments. Treat other people's data, accounts, attention, and money as part
of the affected scope; include those effects in authorization before acting.
Use authorization already present in the task without asking again.

`effects` uses these explicit declarations:

| Effect | What the helper may do |
| --- | --- |
| `local-read` / `local-write` | Read inputs / create or change local outputs. |
| `network-read` / `network-write` | Fetch remote data / send or modify remote data. |
| `account-write` | Change account state, selections, or settings. |
| `spend` | Incur an external charge. |

Declarations cover the helper. Fetching inputs, installing dependencies, or
publishing outputs can add effects; assess that complete task before execution.
No entry grants permission to act on other people or systems.

`bounds.enforced` lists limits the implementation actually checks. It may be
empty. `bounds.operator` lists constraints the caller must apply, including a
resource budget when the helper cannot enforce one. `stop_when` names completion
and failure conditions. Errors end an attempt; further work needs a concrete
reason rather than an automatic retry loop. Builds do not schedule themselves
or automatically expand their scope.

These declarations are a review contract, not a security sandbox. Host
permissions and implementation checks enforce limits. The catalogue validator
checks structure and file references; it cannot prove a helper matches its
declarations or that a user's client displayed the result.

## Add a build

1. Create `skills/<id>/` with a narrow `SKILL.md`, helper, and license. Use the
   GIF build as a working example; copy only what the new task needs.
2. Copy [templates/build.json](templates/build.json) into the package. Replace
   its example text and declare the actual effects. Keep optional resources
   out until there is a reason to add them.
3. Add an evidence record: input/revision, environment, expected outcome,
   observed outcome, and limitations. Label untested client behavior plainly.
4. Add meaningful checks using small fixtures and connect them to CI. Register
   the package and check files in `catalog.json`; registration does not run them.
5. Run `python catalog.py check` and the relevant checks. Open one draft PR
   with exactly one attribution and leave human readback for the human reviewer.

Tests establish the properties they exercise. Observations establish what the
recipient saw in that environment. Review checks the proposed effects and scope.
Keep each claim attached to the evidence that supports it.
