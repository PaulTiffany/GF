// Test host only. This is not an adapter installed into ChatGPT.
import {
  AppBridge,
  PostMessageTransport,
} from "@modelcontextprotocol/ext-apps/app-bridge";

window.mountDashboard = async ({ html, args, opened }) => {
  const viewport = document.createElement("meta");
  viewport.name = "viewport";
  viewport.content = "width=device-width, initial-scale=1";
  document.head.append(viewport);
  const frame = document.createElement("iframe");
  frame.title = "GF custom dashboard";
  frame.setAttribute("sandbox", "allow-scripts");
  frame.style.cssText = "display:block;width:100%;height:1200px;border:0";
  document.body.style.margin = "0";
  document.body.append(frame);
  const bridge = new AppBridge(
    null,
    { name: "GF integration test host", version: "0.1.0" },
    { serverTools: {} },
    { hostContext: { theme: "light" } },
  );
  bridge.oncalltool = async (params) => {
    if (params.name !== "submit_dashboard")
      throw new Error("Only the dashboard callback is exposed");
    return window.callDashboardTool(params);
  };
  bridge.onsizechange = ({ height }) => {
    if (height) frame.style.height = Math.ceil(height) + "px";
  };
  bridge.oninitialized = async () => {
    await bridge.sendToolInput({ arguments: args });
    await bridge.sendToolResult(opened);
  };
  await bridge.connect(
    new PostMessageTransport(frame.contentWindow, frame.contentWindow),
  );
  // Deny external requests in addition to the declared MCP resource CSP.
  frame.srcdoc = html.replace(
    "<head>",
    "<head><meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'\">",
  );
};
