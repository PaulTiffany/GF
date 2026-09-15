import { randomBytes, randomUUID, timingSafeEqual } from "node:crypto";

export function boundedObject(value, limit = 16384) {
  const visit = (item, depth) => {
    if (depth > 8) throw new Error("JSON nesting exceeds eight levels");
    if (item === null || typeof item === "boolean") return;
    if (typeof item === "number" && Number.isFinite(item)) return;
    if (typeof item === "string" && item.length <= 4096) return;
    if (Array.isArray(item) && item.length <= 256) {
      item.forEach((child) => visit(child, depth + 1));
      return;
    }
    if (item && Object.getPrototypeOf(item) === Object.prototype) {
      const entries = Object.entries(item);
      if (entries.length > 128) throw new Error("Too many object fields");
      for (const [key, child] of entries) {
        if (key.length > 128) throw new Error("Object key is too long");
        visit(child, depth + 1);
      }
      return;
    }
    throw new Error("Expected bounded JSON data");
  };
  if (
    !value ||
    Array.isArray(value) ||
    Object.getPrototypeOf(value) !== Object.prototype
  ) {
    throw new Error("State must be a JSON object");
  }
  visit(value, 0);
  const text = JSON.stringify(value);
  if (Buffer.byteLength(text) > limit)
    throw new Error("JSON byte limit exceeded");
  return JSON.parse(text);
}

function canonical(value) {
  if (Array.isArray(value)) return "[" + value.map(canonical).join(",") + "]";
  if (value && typeof value === "object") {
    return (
      "{" +
      Object.keys(value)
        .sort()
        .map((key) => JSON.stringify(key) + ":" + canonical(value[key]))
        .join(",") +
      "}"
    );
  }
  return JSON.stringify(value);
}

export class DashboardStore {
  constructor({
    clock = Date.now,
    capacity = 8,
    validateState = () => {},
  } = {}) {
    this.clock = clock;
    this.capacity = capacity;
    this.validateState = validateState;
    this.panels = new Map();
  }

  open({ title, view = "custom", data = {}, ttl_seconds = 120 }) {
    if (typeof title !== "string" || !title.trim() || title.length > 100)
      throw new Error("Invalid title");
    if (typeof view !== "string" || view.length > 64)
      throw new Error("Invalid view");
    if (!Number.isInteger(ttl_seconds) || ttl_seconds < 5 || ttl_seconds > 180)
      throw new Error("Lifetime must be 5–180 seconds");
    const clean = boundedObject(data, 65536);
    for (const [id, panel] of this.panels) {
      if (panel.expires_at <= this.clock()) {
        this.finish(panel, "expired");
        this.panels.delete(id);
      }
    }
    if (this.panels.size >= this.capacity) {
      const done = [...this.panels].find(
        ([, panel]) => panel.status !== "open",
      );
      if (done) this.panels.delete(done[0]);
    }
    if (this.panels.size >= this.capacity)
      throw new Error("Dashboard capacity reached");
    const panel = {
      panel_id: randomUUID(),
      title,
      view,
      data: clean,
      status: "open",
      nonce: randomBytes(32).toString("hex"),
      expires_at: this.clock() + ttl_seconds * 1000,
      waiter: null,
    };
    this.panels.set(panel.panel_id, panel);
    return {
      ...this.snapshot(panel),
      title,
      data: structuredClone(clean),
      nonce: panel.nonce,
    };
  }

  get(id) {
    const panel = this.panels.get(id);
    if (!panel) throw new Error("Unknown or retired dashboard");
    if (panel.status === "open" && panel.expires_at <= this.clock())
      this.finish(panel, "expired");
    return panel;
  }

  snapshot(panel) {
    return {
      panel_id: panel.panel_id,
      view: panel.view,
      status: panel.status,
      expires_at: panel.expires_at,
      ...(panel.status === "submitted"
        ? { state: structuredClone(panel.state) }
        : {}),
    };
  }

  finish(panel, status, state) {
    panel.status = status;
    if (state !== undefined) panel.state = state;
    if (panel.waiter) panel.waiter(this.snapshot(panel));
    return this.snapshot(panel);
  }

  submit({ panel_id, nonce, decision, state }) {
    const panel = this.get(panel_id);
    if (
      typeof nonce !== "string" ||
      !/^[a-f0-9]{64}$/.test(nonce) ||
      !timingSafeEqual(Buffer.from(nonce), Buffer.from(panel.nonce))
    )
      throw new Error("Invalid dashboard receipt");
    if (!["continue", "cancel"].includes(decision))
      throw new Error("Invalid decision");
    const status = decision === "continue" ? "submitted" : "cancelled";
    const clean = decision === "continue" ? boundedObject(state) : undefined;
    if (decision === "continue") this.validateState(panel, clean);
    if (decision === "cancel" && state !== undefined)
      throw new Error("Cancel must not carry state");
    if (panel.status !== "open") {
      if (
        panel.status === status &&
        canonical(clean) === canonical(panel.state)
      )
        return this.snapshot(panel);
      throw new Error("Dashboard has already closed");
    }
    return this.finish(panel, status, clean);
  }

  wait(id, { seconds = 40, signal } = {}) {
    if (!Number.isInteger(seconds) || seconds < 1 || seconds > 45)
      throw new Error("Wait must be 1–45 seconds");
    const panel = this.get(id);
    if (panel.status !== "open") return Promise.resolve(this.snapshot(panel));
    if (panel.waiter)
      throw new Error("A wait is already active for this dashboard");
    if (signal?.aborted)
      return Promise.resolve(this.finish(panel, "cancelled"));
    return new Promise((resolve) => {
      let timer;
      const complete = (result) => {
        clearTimeout(timer);
        signal?.removeEventListener("abort", abort);
        panel.waiter = null;
        resolve(result);
      };
      const abort = () => this.finish(panel, "cancelled");
      panel.waiter = complete;
      signal?.addEventListener("abort", abort, { once: true });
      timer = setTimeout(
        () => {
          if (panel.expires_at <= this.clock()) this.finish(panel, "expired");
          else complete({ ...this.snapshot(panel), status: "pending" });
        },
        Math.min(seconds * 1000, Math.max(0, panel.expires_at - this.clock())),
      );
    });
  }

  close() {
    for (const panel of this.panels.values())
      if (panel.status === "open") this.finish(panel, "cancelled");
    this.panels.clear();
  }
}
