import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { startClient } from "./client.mjs";

test("real MCP transport serves the app and processes its callback during a held wait", async (t) => {
  const client = await startClient();
  t.after(() => client.close());
  const { tools } = await client.listTools();
  const opener = tools.find((tool) => tool.name === "open_files_dashboard");
  assert.deepEqual(
    tools.find((tool) => tool.name === "submit_dashboard")._meta.ui.visibility,
    ["app"],
  );
  const resource = await client.readResource({
    uri: opener._meta.ui.resourceUri,
  });
  assert.equal(resource.contents[0].mimeType, "text/html;profile=mcp-app");
  assert.ok(resource.contents[0].text.includes("GFDashboard"));
  assert.deepEqual(resource.contents[0]._meta.ui.csp.connectDomains, []);
  const args = JSON.parse(
    await readFile(new URL("../examples/files.json", import.meta.url)),
  );
  const opened = await client.callTool({ name: opener.name, arguments: args });
  assert.equal(opened.isError, undefined);
  assert.equal(opened.structuredContent.status, "open");
  assert.equal(
    JSON.stringify(opened.content).includes(opened._meta["gf/submitNonce"]),
    false,
  );
  assert.equal(
    JSON.stringify(opened.structuredContent).includes(
      opened._meta["gf/submitNonce"],
    ),
    false,
  );
  const panel_id = opened.structuredContent.panel_id;
  let resolved = false;
  const waiting = client
    .callTool({ name: "wait_dashboard", arguments: { panel_id, seconds: 5 } })
    .then((result) => {
      resolved = true;
      return result;
    });
  await client.ping();
  assert.equal(resolved, false);
  const state = {
    selected: ["report"],
    order: ["report", "notes", "measurements"],
  };
  const ack = await client.callTool({
    name: "submit_dashboard",
    arguments: {
      panel_id,
      nonce: opened._meta["gf/submitNonce"],
      decision: "continue",
      state,
    },
  });
  assert.equal(ack.structuredContent.status, "submitted");
  assert.deepEqual((await waiting).structuredContent.state, state);
});

test("invalid callback remains an error and cancellation returns no selected state", async (t) => {
  const client = await startClient();
  t.after(() => client.close());
  const args = JSON.parse(
    await readFile(new URL("../examples/magazine.json", import.meta.url)),
  );
  const opened = await client.callTool({
    name: "open_magazine_dashboard",
    arguments: args,
  });
  const panel_id = opened.structuredContent.panel_id;
  const waiting = client.callTool({
    name: "wait_dashboard",
    arguments: { panel_id, seconds: 5 },
  });
  const invalid = await client.callTool({
    name: "submit_dashboard",
    arguments: {
      panel_id,
      nonce: "0".repeat(64),
      decision: "continue",
      state: {},
    },
  });
  assert.equal(invalid.isError, true);
  const ack = await client.callTool({
    name: "submit_dashboard",
    arguments: {
      panel_id,
      nonce: opened._meta["gf/submitNonce"],
      decision: "cancel",
    },
  });
  assert.equal(ack.structuredContent.status, "cancelled");
  const result = (await waiting).structuredContent;
  assert.equal(result.status, "cancelled");
  assert.equal("state" in result, false);
});
