import { build } from "esbuild";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { resolve } from "node:path";

const root = fileURLToPath(new URL("../", import.meta.url));
mkdirSync(resolve(root, "dist"), { recursive: true });
const built = await build({
  absWorkingDir: root,
  entryPoints: ["assets/bridge.mjs"],
  bundle: true,
  format: "iife",
  globalName: "GFDashboard",
  minify: true,
  write: false,
  metafile: true,
  platform: "browser",
  target: ["es2022"],
  legalComments: "inline",
});
const packages = new Set(
  Object.keys(built.metafile.inputs)
    .map((path) => path.match(/node_modules\/((?:@[^/]+\/)?[^/]+)/)?.[1])
    .filter(Boolean),
);
const notices = [...packages]
  .sort()
  .map((name) => {
    const base = resolve(root, "node_modules", name);
    const file = ["LICENSE", "LICENSE.txt", "LICENSE.md"].find((file) => {
      try {
        readFileSync(resolve(base, file));
        return true;
      } catch {
        return false;
      }
    });
    if (!file) throw new Error(`Missing license for bundled package ${name}`);
    return name + "\n" + readFileSync(resolve(base, file), "utf8");
  })
  .join("\n\n");
if (notices.includes("*/"))
  throw new Error("License needs a different comment delimiter");
const bridge =
  built.outputFiles[0].text +
  "\n/* Bundled dependency licenses\n" +
  notices +
  "\n*/\n";
writeFileSync(resolve(root, "dist/bridge.js"), bridge);
writeFileSync(resolve(root, "dist/THIRD_PARTY_LICENSES.txt"), notices);
for (const view of ["magazine", "files"]) {
  const source = readFileSync(resolve(root, "assets", `${view}.html`), "utf8");
  if (source.split("<!-- GF_BRIDGE -->").length !== 2)
    throw new Error("Missing or duplicate bridge marker");
  const html = source
    .replace(
      "<!-- GF_BRIDGE -->",
      () =>
        "<script>" + bridge.replaceAll("</script", "<\\/script") + "</script>",
    )
    .replace(
      "<!-- GF_STYLE -->",
      () =>
        "<style>" +
        readFileSync(resolve(root, "assets/style.css"), "utf8") +
        "</style>",
    );
  if (Buffer.byteLength(html) > 1048576)
    throw new Error("Dashboard exceeds 1 MiB");
  writeFileSync(resolve(root, "dist", `${view}.html`), html);
}
console.log("Built two custom dashboards and the reusable return bridge.");
