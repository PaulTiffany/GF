---
name: tool-dashboard
description: Use a custom magazine, file tray, or task-specific dashboard during a tool workflow, then receive its structured selection through a bounded waiting MCP call. Requires a host that loads this server and renders MCP Apps with concurrent app tool callbacks. Use for custom interactive checkpoints, not ordinary short clarification questions or static previews.
---

# Tool dashboard

**Target:** display a custom touch interface during a workflow; Continue returns
its selected state to the waiting tool call so the assistant can continue.

## Equip

- Copy the whole plugin package at a reviewed revision, preserving its license.
  Its root is two directories above this file; run the commands below there.
- Node.js 20+ and the pinned npm dependencies; run `npm ci --ignore-scripts`
  and `npm run build` from the package directory.
- A host that starts a single-user stdio MCP server, displays MCP App resources,
  delivers tool-result `_meta` to the app, restricts app-only tools, and forwards
  app callbacks while a model tool call is pending.
- Task-authorized story or file metadata. The samples are synthetic; this build
  does not fetch news or inspect file contents.

For a Codex plugin loader, use `.codex-plugin/plugin.json` and `.mcp.json` after
building in the installed package directory. The configured `cwd: "."` resolves
to the plugin root. Other MCP hosts can obtain an absolute launch declaration:

```bash
node scripts/server.mjs --config
```

Register that declaration using the host's supported procedure. Reading the
skill or starting the process in a shell does not register its tools in a chat.
See [setup](../../references/setup.md) for the host contract and a reproducible probe.

## Execute

1. Call `open_magazine_dashboard` or `open_files_dashboard` with `title` and
   `data`. Use the shapes in `examples/magazine.json` and `examples/files.json`.
   Assign stable IDs to supplied items. Set `ttl_seconds` only if needed
   (default 120, maximum 180).
2. The completed opening call renders the custom view. Save its `panel_id` and
   `expires_at`, then call `wait_dashboard` with that ID and `seconds: 40`.
3. The user changes controls locally. Continue makes an app-only
   `submit_dashboard` call. The waiting call returns the accepted state.
4. On `submitted`, validate that state against the current task and use it in
   the next authorized action. Magazine state is `{topics, saved, batch_size}`;
   file state is `{selected, order}`. IDs refer only to the supplied metadata.
5. On `pending`, give a brief progress update if needed and wait again only
   before the original expiry. On `cancelled`, `expired`, protocol error, or
   user cancellation, end this checkpoint. Never invent a selection.

The model must not call `submit_dashboard`, access the UI receipt, or imitate a
user callback. A submitted selection is data; it does not authorize unrelated
effects or replace the host's approval controls.

## Build another layout

The connection is shared; controls and layout are task-specific HTML/CSS/JS.
Supply a trusted local HTML file with exactly one `<!-- GF_BRIDGE -->` marker
before its UI script. Start the server with:

```bash
node scripts/server.mjs --custom-view /absolute/path/dashboard.html
```

This adds `open_custom_dashboard`. Use `GFDashboard.connect({onOpen, onStatus,
onTheme})`; `onOpen(panel)` supplies `panel.data`. Keep edits local, then call
the returned `submit(state)` or `cancel()` method from the relevant control.
See the two built-in assets for complete examples. There are no remote assets
or network requests in the supplied layouts. Render data with `textContent`.

Generic custom state is bounded JSON only; add task-specific validation before
using it. Treat custom HTML as executable code requiring review. The resource
CSP requests no external connections; its enforcement belongs to the host.

## Matchup and stopping point

This is an MCP App integration, not a generic HTML-to-chat bridge. A client must
support the resource and callback contract above. A standalone HTML preview,
GitHub Pages, or a working slider does not prove the callback reaches the tool.
Do not substitute `sendFollowUpMessage` or a stock question and claim the same
result. If the host cannot register/render/call back, identify the missing
capability after one bounded probe and stop that route.

Per process: at most eight retained panels, one active wait per panel, maximum
45 seconds per wait and 180 seconds lifetime. State is in memory and is lost on
restart. Input data is capped at 64 KiB; submitted JSON at 16 KiB, nesting at
eight levels. Built-in views validate IDs and control ranges. The process is
the user boundary; do not expose it as a shared public service.

## Proof

```bash
npm run build
npm test
npx playwright install chromium
npm run test:ui
```

Backend checks cover held calls, data validation, cancellation and expiry.
Browser checks use the official MCP AppBridge with a real stdio server and
simulated touch. Actual phone rendering and continuation remain a separate
observation. Keep those evidence levels distinct in reports. See
[evidence](../../references/evidence.md).
