import test from "node:test";
import assert from "node:assert/strict";
import { readFile, mkdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { build } from "esbuild";
import { chromium } from "playwright";
import { startClient } from "./client.mjs";

const root = fileURLToPath(new URL("../", import.meta.url));
const bundle = await build({
  absWorkingDir: root,
  entryPoints: ["tests/host.mjs"],
  bundle: true,
  format: "iife",
  platform: "browser",
  target: ["es2022"],
  write: false,
});
await mkdir(new URL("../test-output/", import.meta.url), { recursive: true });

async function panel(t, view, width = 390) {
  const client = await startClient();
  t.after(() => client.close());
  const browser = await chromium.launch({ headless: true });
  t.after(() => browser.close());
  const page = await browser.newPage({
    viewport: { width, height: 844 },
    hasTouch: true,
    isMobile: true,
  });
  page.setDefaultTimeout(10000);
  const errors = [],
    requests = [],
    callbacks = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.route("**/*", (route) => {
    requests.push(route.request().url());
    return route.abort();
  });
  const args = JSON.parse(
    await readFile(new URL(`../examples/${view}.json`, import.meta.url)),
  );
  const opened = await client.callTool({
    name: `open_${view}_dashboard`,
    arguments: args,
  });
  assert.equal(opened.isError, undefined);
  const { tools } = await client.listTools();
  const uri = tools.find((tool) => tool.name === `open_${view}_dashboard`)._meta
    .ui.resourceUri;
  const html = (await client.readResource({ uri })).contents[0].text;
  let resolved = false;
  const waiting = client
    .callTool({
      name: "wait_dashboard",
      arguments: {
        panel_id: opened.structuredContent.panel_id,
        seconds: 40,
      },
    })
    .then((result) => {
      resolved = true;
      return result.structuredContent;
    });
  // Keep a rejection handler attached while browser assertions are in flight.
  waiting.catch(() => {});
  await client.ping();
  assert.equal(resolved, false);
  await page.exposeFunction("callDashboardTool", (params) => {
    callbacks.push(params.name);
    return client.callTool(params);
  });
  await page.addScriptTag({ content: bundle.outputFiles[0].text });
  await page.evaluate((payload) => window.mountDashboard(payload), {
    html,
    args,
    opened,
  });
  const frame = page.frameLocator("iframe");
  await frame.locator("#continue:enabled").waitFor();
  return {
    page,
    frame,
    waiting,
    callbacks,
    assertHeld: () => assert.equal(resolved, false),
    async record(name, state) {
      assert.deepEqual(errors, []);
      assert.deepEqual(requests, []);
      const fits = await frame
        .locator("body")
        .evaluate((body) => body.scrollWidth <= window.innerWidth);
      assert.equal(fits, true, "dashboard must fit a narrow viewport");
      assert.equal(
        await frame.locator("body").evaluate(() => window.innerWidth),
        width,
      );
      await frame
        .locator("main")
        .screenshot({ path: `${root}/test-output/${name}.png` });
      await writeFile(
        `${root}/test-output/${name}.json`,
        JSON.stringify(
          {
            environment:
              "headless Chromium with official MCP AppBridge; simulated touch",
            browser: browser.version(),
            width,
            callbacks,
            state,
            phone_observed: false,
          },
          null,
          2,
        ) + "\n",
      );
    },
  };
}

test(
  "magazine touch controls return interests, saved story and batch size to the held tool",
  { timeout: 30000 },
  async (t) => {
    const p = await panel(t, "magazine", 320);
    await p.frame.getByRole("button", { name: "Gardens", exact: true }).tap();
    await p.frame.getByRole("button", { name: "Research", exact: true }).tap();
    await p.frame.getByLabel("Keep this story").tap();
    const slider = p.frame.locator("#batch");
    await slider.focus();
    await slider.press("End");
    p.assertHeld();
    assert.deepEqual(p.callbacks, []);
    await p.frame.getByRole("button", { name: "Continue", exact: true }).tap();
    const receipt = await p.waiting;
    assert.equal(receipt.status, "submitted");
    assert.deepEqual(receipt.state, {
      topics: ["Tools"],
      saved: ["small-tools"],
      batch_size: 8,
    });
    await p.frame.getByText("Selection returned", { exact: true }).waitFor();
    assert.deepEqual(p.callbacks, ["submit_dashboard"]);
    await p.record("magazine-submitted", receipt.state);
  },
);

test(
  "file cards select and reorder actual IDs before releasing the tool",
  { timeout: 30000 },
  async (t) => {
    const p = await panel(t, "files");
    await p.frame.getByLabel("Select report.pdf", { exact: true }).tap();
    await p.frame
      .getByRole("button", { name: "Move report.pdf earlier", exact: true })
      .tap();
    p.assertHeld();
    assert.deepEqual(p.callbacks, []);
    await p.frame.getByRole("button", { name: "Continue", exact: true }).tap();
    const receipt = await p.waiting;
    assert.equal(receipt.status, "submitted");
    assert.deepEqual(receipt.state, {
      selected: ["report"],
      order: ["report", "notes", "measurements"],
    });
    await p.frame.getByText("Selection returned", { exact: true }).waitFor();
    await p.record("files-submitted", receipt.state);
  },
);

test(
  "the custom Cancel control releases a wait without selected state",
  { timeout: 30000 },
  async (t) => {
    const p = await panel(t, "files", 320);
    await p.frame.getByLabel("Select notes.md", { exact: true }).tap();
    p.assertHeld();
    await p.frame.getByRole("button", { name: "Cancel", exact: true }).tap();
    const receipt = await p.waiting;
    assert.equal(receipt.status, "cancelled");
    assert.equal("state" in receipt, false);
    await p.frame.getByText("Cancelled", { exact: true }).waitFor();
    await p.record("files-cancelled", null);
  },
);
