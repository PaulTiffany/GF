# Build 03 evidence

Date: 2026-09-15. Tested implementation:
[`1dc1b9d`](https://github.com/PaulTiffany/GF/commit/1dc1b9d248106f9b5ffe0d9ad9e673fc3541d5de).
All eight backend/transport tests and all three browser tests passed in
[run 34990560997](https://github.com/PaulTiffany/GF/actions/runs/34990560997).
The downloaded evidence archive matched its published SHA-256 digest; the two
submitted dashboard screenshots were inspected. The captured states and
environment are preserved in [ci-result.json](ci-result.json).

| Layer | Evidence | Boundary |
| --- | --- | --- |
| Store and validation | `npm test`: real held wait, identical retry, wrong receipt, timeout, abort, expiry, capacity and payload limits, supplied-ID checks | Tests the bounded state machine |
| MCP transport | `npm test`: official SDK client and server over stdio; ping and callback complete while wait is pending | Tests concurrent protocol handling |
| Browser UI | Three passing CI tests: official AppBridge, sandboxed iframe, real MCP stdio calls, simulated touch at 320/390 px | Establishes the tested browser flow; does not establish phone compatibility |
| Phone host | No observation yet for this build | Plugin registration, rendering, concurrent callbacks and continuation still need the phone probe |

The initial local build and all eight backend/transport tests passed on Linux
with Node 24.19.0. CI uses Node 22. The local browser download failed at the
Playwright CDN with timeouts/gateway errors, so no local browser success is
claimed. The dashboard CI job installed Chromium 143.0.7499.4 and passed the
full browser path. Successful runs upload screenshots
and JSON receipts in `dashboard-evidence`; those records explicitly say
`phone_observed: false`.

Browser scenarios verify that editing does not call the server or release the
wait, Continue returns the selected values, and Cancel discards local edits.
They use three synthetic stories and three synthetic file records. The test
host denies external resource requests and exposes only the submit callback.
The range is exercised with keyboard input; buttons and checkboxes use
simulated taps. Physical device touch behavior is untested.

The earlier phone conversation established that ordinary custom HTML controls
could change local state, but its chat-interaction bridge was unavailable.
That is the motivation for this build, not proof that this new bridge is
installed. GIF attachment/player observations belong to Build 01.

## Reproduce

From a fresh copy of this package:

```bash
npm ci --ignore-scripts
npm run build
npm test
npx playwright install --with-deps chromium
npm run test:ui
```

The browser host in `tests/host.mjs` is a test harness, not a ChatGPT client
extension or a deployed service. Both layouts use the same bundled App bridge.
For the real client acceptance check, follow [setup](setup.md).
