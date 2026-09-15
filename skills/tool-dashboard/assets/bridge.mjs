import { App } from "@modelcontextprotocol/ext-apps";

// A custom layout supplies its own controls and state; this owns the return path.
export function connect({ onOpen, onStatus = () => {}, onTheme = () => {} }) {
  const app = new App({ name: "GF dashboard", version: "0.1.0" }, {});
  let panel,
    nonce,
    submitted = false;
  app.onhostcontextchanged = (context) => onTheme(context.theme);
  app.ontoolresult = (result) => {
    const next = result.structuredContent;
    if (!next?.panel_id || !result._meta?.["gf/submitNonce"]) return;
    if (panel) return;
    panel = next;
    nonce = result._meta["gf/submitNonce"];
    onOpen(structuredClone(panel));
    onStatus("ready");
  };
  app.ontoolcancelled = () => {
    submitted = true;
    onStatus("cancelled");
  };
  app
    .connect()
    .then(() => onTheme(app.getHostContext()?.theme))
    .catch(() => onStatus("unavailable"));

  async function finish(decision, state) {
    if (!panel || submitted) return;
    if (Date.now() >= panel.expires_at) {
      submitted = true;
      onStatus("expired");
      return;
    }
    submitted = true;
    onStatus("submitting");
    try {
      const result = await app.callServerTool({
        name: "submit_dashboard",
        arguments: {
          panel_id: panel.panel_id,
          nonce,
          decision,
          ...(decision === "continue" ? { state } : {}),
        },
      });
      if (
        result.isError ||
        !["submitted", "cancelled"].includes(result.structuredContent?.status)
      ) {
        onStatus("unconfirmed");
      } else {
        onStatus(result.structuredContent.status);
      }
    } catch (_) {
      onStatus("unconfirmed");
    }
  }
  return {
    submit: (state) => finish("continue", state),
    cancel: () => finish("cancel"),
  };
}
