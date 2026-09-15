# Host setup and acceptance

Build the package with `npm ci --ignore-scripts` and `npm run build`. The source
package carries a Codex plugin manifest and a stdio MCP declaration; it does
not install itself. Its dependencies and generated `dist` files must be present
in the directory from which the registered server runs. It needs no credentials,
listening port or public URL. `node scripts/server.mjs --config` prints absolute
paths for hosts that use a standard MCP JSON declaration.

The plugin uses `cwd: "."` so Node resolves `scripts/server.mjs` from the plugin
root. This follows the [Codex plugin MCP configuration resolver at the inspected
revision](https://github.com/openai/codex/blob/7784318b5f7fa35728d41ffa13e2a5821ebb4d75/codex-rs/codex-mcp/src/plugin_config.rs).
It does not assume an undocumented environment-variable expansion.

## Required return path

The host must:

1. Run one server process per user/session and retain that process between calls.
2. Render the opening tool's `_meta.ui.resourceUri` using MIME
   `text/html;profile=mcp-app` in an isolated MCP App iframe.
3. Complete `ui/initialize`, send `ui/notifications/tool-input` and then
   `ui/notifications/tool-result`, preserving app-private result `_meta`.
4. Keep app-only tools out of the model's callable tools and forward the app's
   `tools/call` for `submit_dashboard` to the same server while `wait_dashboard`
   is pending. A host that serializes all calls cannot complete this interaction.
5. Deliver the wait's final tool result to the assistant and respect cancellation.

These are the [official MCP App integration primitives](https://developers.openai.com/plugins/build/chatgpt-ui).
The server includes compatibility metadata for OpenAI hosts, but metadata does
not establish that any particular phone session supports the integration.

The open and wait calls are separate because a host may not show a tool's UI
until that opening call has completed. UI controls do not send chat messages.
No UI response can interrupt or expose private model reasoning; it returns a
normal tool result at an explicit workflow checkpoint.

## One phone probe

After the host registers the built plugin, the assistant opens
`examples/magazine.json` through `open_magazine_dashboard`, then calls
`wait_dashboard`. The user deselects Gardens and Research, keeps the remaining
Tools story, chooses a batch size, and taps Continue. The assistant should
receive only Tools, the saved `small-tools` ID, and the chosen number in the
wait result, then continue its task using that state. No download, re-upload,
typed reply, or follow-up chat message is part of this probe.

Record client/platform, plugin revision, whether the dashboard appeared,
whether controls worked, the actual wait receipt and whether the workflow
continued. Stop after an unsupported bridge, expiry or cancellation; report
the exact missing part. Do not convert a browser test into a phone observation.

## Trust and scope

The random submission receipt lives in tool-result `_meta`, which a conforming
host delivers to the app without adding it to model context. It binds a
callback to a particular panel. App-only visibility and `_meta` separation are
host responsibilities, not independent authentication. Anyone controlling the
stdio transport can see that metadata and send calls. A receipt is not proof
of a physical click, identity, or authorization for later side effects.

The build intentionally provides no shared HTTP service, cross-user session
management, general command dispatcher, automatic news fetching or file writes.
Additional hosts or transports must implement their own authentication and
isolation. UI selections remain untrusted task data. The server's JSON bounds
apply after transport parsing; use host process/memory limits when needed.

## Custom HTML

`--custom-view` reads only the explicitly provided local file and supplies the
bundled bridge at its marker. The file and resulting view must each fit in
1 MiB. The built-in state validators know magazine and file IDs; a custom view
gets only generic JSON limits until its consuming workflow validates semantics.

No external resources are requested by the resource CSP. That is a host policy
request, not an OS sandbox for the Node process or a sanitizer for supplied HTML.
Review custom code before registering it. The generated bundles preserve their
dependency notices in both the JavaScript and `dist/THIRD_PARTY_LICENSES.txt`.
