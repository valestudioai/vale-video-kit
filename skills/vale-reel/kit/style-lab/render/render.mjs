// Render an HTML animation to PNG frames with headless Chrome over the DevTools protocol (no npm installs).
// The page must define window.seek(t) (seconds) that puts every animation at time t, and may set
// window.DURATION (seconds). Frames are written as frames/%05d.png; encode them with ffmpeg afterwards.
//
// Usage: node render.mjs <page.html> <outDir> [fps=30] [width=1080] [height=1920] [--transparent]
import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync, rmSync } from "node:fs";
import { resolve, join } from "node:path";
import { pathToFileURL } from "node:url";
import { tmpdir } from "node:os";

const [, , page, outDir, fpsArg, wArg, hArg, ...flags] = process.argv;
const fps = Number(fpsArg || 30), W = Number(wArg || 1080), H = Number(hArg || 1920);
const transparent = flags.includes("--transparent");
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const port = 9300 + Math.floor(Math.random() * 600);
const profile = join(tmpdir(), "stylelab-chrome-" + port);

const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`,
  "--hide-scrollbars", "--disable-gpu", "--force-device-scale-factor=1", "--allow-file-access-from-files",
  "--autoplay-policy=no-user-gesture-required", `--window-size=${W},${H}`, "about:blank"], { stdio: "ignore" });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function target() {
  for (let i = 0; i < 80; i++) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
      const p = list.find((t) => t.type === "page");
      if (p) return p.webSocketDebuggerUrl;
    } catch {}
    await sleep(150);
  }
  throw new Error("Chrome did not start");
}

const ws = new WebSocket(await target());
await new Promise((r) => ws.addEventListener("open", r, { once: true }));
let id = 0;
const pending = new Map();
ws.addEventListener("message", (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { const { ok, ko } = pending.get(m.id); pending.delete(m.id); m.error ? ko(new Error(JSON.stringify(m.error))) : ok(m.result); }
});
const send = (method, params = {}) => new Promise((ok, ko) => { const i = ++id; pending.set(i, { ok, ko }); ws.send(JSON.stringify({ id: i, method, params })); });
const evalJs = async (expression) => {
  const r = await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text);
  return r.result.value;
};

await send("Page.enable");
await send("Runtime.enable");
await send("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: 1, mobile: false });
if (transparent) await send("Emulation.setDefaultBackgroundColorOverride", { color: { r: 0, g: 0, b: 0, a: 0 } });
await send("Page.navigate", { url: pathToFileURL(resolve(page)).href });
for (let i = 0; i < 100; i++) { if ((await evalJs("document.readyState")) === "complete") break; await sleep(100); }
await evalJs("document.fonts.ready.then(() => true)");
await sleep(200);
const duration = await evalJs("window.DURATION || 3");
const n = Math.round(duration * fps);

rmSync(outDir, { recursive: true, force: true });
mkdirSync(outDir, { recursive: true });
for (let f = 0; f < n; f++) {
  await evalJs(`Promise.resolve(window.seek(${f / fps})).then(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))))`);
  const shot = await send("Page.captureScreenshot", { format: "png", fromSurface: true, captureBeyondViewport: false });
  writeFileSync(join(outDir, String(f).padStart(5, "0") + ".png"), Buffer.from(shot.data, "base64"));
}
ws.close();
chrome.kill();
await sleep(400);
try { rmSync(profile, { recursive: true, force: true }); } catch {}
console.log(`${n} frames, ${duration}s @ ${fps}fps -> ${outDir}`);
