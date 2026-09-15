import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { fileURLToPath } from "node:url";

export async function startClient(args = []) {
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [
      fileURLToPath(new URL("../scripts/server.mjs", import.meta.url)),
      ...args,
    ],
    stderr: "inherit",
  });
  const client = new Client({ name: "gf-dashboard-test", version: "0.1.0" });
  await client.connect(transport);
  return client;
}
