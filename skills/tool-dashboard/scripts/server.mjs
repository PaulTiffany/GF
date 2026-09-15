import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import { resolve } from "node:path";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod/v3";
import { DashboardStore } from "./core.mjs";
import { validateData, validateState } from "./views.mjs";

const root = fileURLToPath(new URL("../", import.meta.url));
const MIME = "text/html;profile=mcp-app";
const receiptSchema = {
  panel_id: z.string(),
  view: z.string(),
  status: z.enum(["open", "pending", "submitted", "cancelled", "expired"]),
  expires_at: z.number(),
  state: z.record(z.unknown()).optional(),
};

function success(result, meta) {
  return {
    structuredContent: result,
    content: [{ type: "text", text: JSON.stringify(result) }],
    ...(meta ? { _meta: meta } : {}),
  };
}

export function createDashboardServer({ customView } = {}) {
  const store = new DashboardStore({ validateState });
  const views = new Map();
  for (const name of ["magazine", "files", ...(customView ? ["custom"] : [])]) {
    let html = readFileSync(
      name === "custom" ? customView : resolve(root, "dist", `${name}.html`),
      "utf8",
    );
    if (Buffer.byteLength(html) > 1048576)
      throw new Error("View exceeds 1 MiB");
    if (name === "custom") {
      if (html.split("<!-- GF_BRIDGE -->").length !== 2)
        throw new Error("Custom HTML needs exactly one GF_BRIDGE marker");
      html = html.replace(
        "<!-- GF_BRIDGE -->",
        () =>
          "<script>" +
          readFileSync(resolve(root, "dist/bridge.js"), "utf8").replaceAll(
            "</script",
            "<\\/script",
          ) +
          "</script>",
      );
    }
    if (Buffer.byteLength(html) > 1048576)
      throw new Error("Built view exceeds 1 MiB");
    const hash = createHash("sha256").update(html).digest("hex");
    views.set(name, {
      uri: `ui://gf-dashboard/${name}-${hash.slice(0, 16)}.html`,
      html,
    });
  }
  const server = new McpServer(
    { name: "gf-tool-dashboard", version: "0.1.0" },
    {
      instructions:
        "For a custom dashboard: call an open_*_dashboard tool, then wait_dashboard for its panel_id. The UI submits its state through submit_dashboard. Only submitted means a selection was received. Pending permits another bounded wait before expires_at. Cancelled or expired ends the checkpoint. Do not call submit_dashboard as the model or fabricate a user selection. Validate returned state against the task before subsequent actions.",
    },
  );
  const protectedHandler =
    (handler) =>
    async (...args) => {
      try {
        return await handler(...args);
      } catch (error) {
        return {
          isError: true,
          content: [{ type: "text", text: error.message }],
        };
      }
    };
  for (const [name, view] of views) {
    server.registerResource(
      `dashboard-${name}`,
      view.uri,
      { mimeType: MIME },
      async () => ({
        contents: [
          {
            uri: view.uri,
            mimeType: MIME,
            text: view.html,
            _meta: {
              ui: {
                prefersBorder: false,
                csp: { connectDomains: [], resourceDomains: [] },
              },
              "openai/widgetCSP": { connect_domains: [], resource_domains: [] },
            },
          },
        ],
      }),
    );
    server.registerTool(
      `open_${name}_dashboard`,
      {
        title: `Open ${name} dashboard`,
        description: `Display a custom ${name} panel, then call wait_dashboard with the returned panel_id. This opens a UI; it does not fetch news or operate on files.`,
        inputSchema: {
          title: z.string().min(1).max(100),
          data: z.record(z.unknown()),
          ttl_seconds: z.number().int().min(5).max(180).default(120),
        },
        outputSchema: {
          ...receiptSchema,
          title: z.string(),
          data: z.record(z.unknown()),
        },
        annotations: {
          readOnlyHint: false,
          destructiveHint: false,
          idempotentHint: false,
          openWorldHint: false,
        },
        _meta: {
          ui: { resourceUri: view.uri, visibility: ["model"] },
          "openai/outputTemplate": view.uri,
          "openai/toolInvocation/invoking": "Opening dashboard",
          "openai/toolInvocation/invoked": "Dashboard ready",
        },
      },
      protectedHandler(async (args) => {
        validateData(name, args.data);
        const { nonce, ...panel } = store.open({ ...args, view: name });
        return success(panel, { "gf/submitNonce": nonce });
      }),
    );
  }
  server.registerTool(
    "wait_dashboard",
    {
      title: "Wait for dashboard",
      description:
        "Hold this workflow for a displayed dashboard. Returns the submitted state, cancelled, expired, or pending after a bounded wait. Never treat pending as a user choice.",
      inputSchema: {
        panel_id: z.string(),
        seconds: z.number().int().min(1).max(45).default(40),
      },
      outputSchema: receiptSchema,
      annotations: {
        readOnlyHint: false,
        destructiveHint: false,
        openWorldHint: false,
      },
      _meta: { ui: { visibility: ["model"] } },
    },
    protectedHandler(async ({ panel_id, seconds }, extra) =>
      success(await store.wait(panel_id, { seconds, signal: extra.signal })),
    ),
  );
  server.registerTool(
    "submit_dashboard",
    {
      title: "Submit dashboard selection",
      description:
        "UI-only: complete or cancel the displayed dashboard. The model must not synthesize this call.",
      inputSchema: {
        panel_id: z.string(),
        nonce: z.string().regex(/^[a-f0-9]{64}$/),
        decision: z.enum(["continue", "cancel"]),
        state: z.record(z.unknown()).optional(),
      },
      outputSchema: receiptSchema,
      annotations: {
        readOnlyHint: false,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
      _meta: {
        ui: { visibility: ["app"] },
        "openai/widgetAccessible": true,
        "openai/visibility": "private",
      },
    },
    protectedHandler(async (args) => success(store.submit(args))),
  );
  server.server.onclose = () => store.close();
  return { server, store, views };
}

if (
  process.argv[1] &&
  resolve(process.argv[1]) === fileURLToPath(import.meta.url)
) {
  const args = process.argv.slice(2);
  if (args[0] === "--config" && args.length === 1) {
    process.stdout.write(
      JSON.stringify(
        {
          mcpServers: {
            "gf-dashboard": {
              command: process.execPath,
              args: [fileURLToPath(import.meta.url)],
            },
          },
        },
        null,
        2,
      ) + "\n",
    );
  } else {
    if (args.length && (args.length !== 2 || args[0] !== "--custom-view"))
      throw new Error("Use --config or --custom-view /absolute/view.html");
    const { server } = createDashboardServer({ customView: args[1] });
    await server.connect(new StdioServerTransport());
  }
}
