import test from "node:test";
import assert from "node:assert/strict";
import { DashboardStore, boundedObject } from "../scripts/core.mjs";
import { validateData, validateState } from "../scripts/views.mjs";

const open = (store) => store.open({ title: "A checkpoint" });
const submit = (store, panel, state = { selected: ["one"] }) =>
  store.submit({
    panel_id: panel.panel_id,
    nonce: panel.nonce,
    decision: "continue",
    state,
  });

test("a held wait receives a cloned state; an identical retry is idempotent", async () => {
  const store = new DashboardStore();
  const panel = open(store);
  const waiting = store.wait(panel.panel_id);
  const state = { selected: ["one"], count: 2 };
  const receipt = submit(store, panel, state);
  state.selected.push("changed");
  assert.deepEqual((await waiting).state, { selected: ["one"], count: 2 });
  assert.deepEqual(
    submit(store, panel, { count: 2, selected: ["one"] }),
    receipt,
  );
  assert.throws(
    () => submit(store, panel, { selected: ["two"] }),
    /already closed/,
  );
  receipt.state.selected.push("also changed");
  assert.deepEqual((await store.wait(panel.panel_id)).state, {
    selected: ["one"],
    count: 2,
  });
  store.close();
});

test("wrong panel receipt cannot submit or release another panel", async () => {
  const store = new DashboardStore();
  const a = open(store),
    b = open(store);
  const waiting = store.wait(a.panel_id);
  assert.throws(
    () => submit(store, { ...a, nonce: b.nonce }),
    /Invalid dashboard receipt/,
  );
  assert.throws(() => store.wait(a.panel_id), /already active/);
  assert.equal(store.get(a.panel_id).status, "open");
  store.submit({ ...a, decision: "cancel" });
  assert.equal((await waiting).status, "cancelled");
  assert.equal(store.get(b.panel_id).status, "open");
  store.close();
});

test("a wait timeout stays pending and accepts a later submission", async () => {
  const store = new DashboardStore();
  const panel = open(store);
  const result = await store.wait(panel.panel_id, { seconds: 1 });
  assert.equal(result.status, "pending");
  assert.equal("state" in result, false);
  const waiting = store.wait(panel.panel_id);
  submit(store, panel);
  assert.equal((await waiting).status, "submitted");
  store.close();
});

test("abort, expiry and process close resolve waits without a selection", async () => {
  let now = Date.now();
  const store = new DashboardStore({ clock: () => now });
  const aborted = open(store),
    expired = open(store),
    closed = open(store);
  const controller = new AbortController();
  const a = store.wait(aborted.panel_id, { signal: controller.signal });
  controller.abort();
  assert.equal((await a).status, "cancelled");
  const b = store.wait(expired.panel_id);
  now += 120000;
  assert.equal(store.get(expired.panel_id).status, "expired");
  assert.equal((await b).status, "expired");
  assert.throws(() => submit(store, expired), /already closed/);
  now -= 120000;
  const c = store.wait(closed.panel_id);
  store.close();
  assert.deepEqual(Object.keys(await c).sort(), [
    "expires_at",
    "panel_id",
    "status",
    "view",
  ]);
});

test("capacity, lifetime and payload limits end invalid attempts", () => {
  const store = new DashboardStore({ capacity: 1 });
  const panel = open(store);
  assert.throws(() => open(store), /capacity/);
  assert.throws(
    () => store.open({ title: "Too long", ttl_seconds: 181 }),
    /Lifetime/,
  );
  assert.throws(() => store.wait(panel.panel_id, { seconds: 46 }), /Wait/);
  assert.throws(
    () => boundedObject({ text: "x".repeat(4097) }),
    /bounded JSON/,
  );
  assert.throws(
    () => boundedObject({ values: Array(257).fill(0) }),
    /bounded JSON/,
  );
  assert.throws(
    () => boundedObject({ text: "é".repeat(30) }, 32),
    /byte limit/,
  );
  assert.throws(
    () => boundedObject({ value: Number.POSITIVE_INFINITY }),
    /bounded JSON/,
  );
  assert.throws(() => boundedObject([]), /JSON object/);
  let nested = {};
  for (let n = 0; n < 10; n++) nested = { nested };
  assert.throws(() => boundedObject(nested), /nesting/);
  store.submit({ ...panel, decision: "cancel" });
  assert.ok(open(store).panel_id);
  store.close();
});

test("built-in states are restricted to supplied items and meaningful controls", () => {
  const store = new DashboardStore({ validateState });
  const data = {
    files: [
      { id: "a", title: "a.txt" },
      { id: "b", title: "b.txt" },
    ],
  };
  validateData("files", data);
  const panel = store.open({ title: "Files", view: "files", data });
  assert.throws(
    () => submit(store, panel, { selected: ["unknown"], order: ["a", "b"] }),
    /unknown/,
  );
  assert.throws(
    () => submit(store, panel, { selected: [], order: ["a"] }),
    /every supplied/,
  );
  assert.throws(
    () => submit(store, panel, { selected: [], order: ["a", "a"] }),
    /duplicate/,
  );
  assert.equal(
    submit(store, panel, { selected: ["b"], order: ["b", "a"] }).status,
    "submitted",
  );
  const magazine = store.open({
    title: "Reading",
    view: "magazine",
    data: {
      topics: ["Tools"],
      articles: [{ id: "story", title: "A story", topic: "Tools" }],
    },
  });
  assert.throws(
    () =>
      submit(store, magazine, { topics: ["Other"], saved: [], batch_size: 1 }),
    /unknown/,
  );
  assert.throws(() =>
    submit(store, magazine, { topics: [], saved: [], batch_size: 9 }),
  );
  assert.equal(
    submit(store, magazine, {
      topics: ["Tools"],
      saved: ["story"],
      batch_size: 3,
    }).status,
    "submitted",
  );
  assert.throws(
    () => validateData("files", { files: [data.files[0], data.files[0]] }),
    /Duplicate/,
  );
  store.close();
});
