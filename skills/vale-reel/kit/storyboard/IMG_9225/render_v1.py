"""Render IMG_9225 exactly as approved in storyboard v1 (Vale Storyboard, approved 2026-10-17).

  1. base.mp4: the approved cut of renders/IMG_9225_master.mov, Vale Warm Natural LUT, speaker shifted down 700px
     during the split (beats 4 to 7)
  2. timeline.html: one transparent overlay for the whole edit (captions, prompt bar, cards, split panel,
     handwritten card, notification, calendar), captured frame by frame with style-lab/render/render.mjs
  3. sfx.wav: the kept Style Lab sounds at their edit times (synthesised in code)
  4. IMG_9225_vale_v1.mp4: base + overlay + voice + sounds

Usage: python3 storyboard/IMG_9225/render_v1.py [--skip-frames]
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = HERE / "v1" / "render"
OUT.mkdir(parents=True, exist_ok=True)
os.environ["PATH"] = str(Path.home() / ".local/bin") + os.pathsep + os.environ["PATH"]
MASTER = ROOT / "renders/IMG_9225_master.mov"
LUT = ROOT / "presets/look/Vale_Warm_Natural.cube"
FPS = 30
pieces = json.loads((ROOT / "transcript/IMG_9225/frames.json").read_text())["pieces"]
words = json.loads((ROOT / "transcript/IMG_9225/words.json").read_text())["words"]
TOTAL = pieces[-1]["time"] + pieces[-1]["sourceOut"] - pieces[-1]["sourceIn"]
NFR = round(TOTAL * FPS)


def E(t):
    """Raw seconds -> edit seconds (a time inside a removed gap snaps to the next kept piece)."""
    for p in pieces:
        if t < p["sourceIn"]:
            return p["time"]
        if t <= p["sourceOut"]:
            return p["time"] + t - p["sourceIn"]
    return TOTAL


def kept(w):
    m = (w["start"] + w["end"]) / 2
    return any(p["sourceIn"] <= m <= p["sourceOut"] for p in pieces)


r = lambda x: round(x, 3)

# ------------------------------------------------------------------ the plan in edit time (anchors are raw word times)
CARDS = [
    {"a": E(9.178), "b": E(10.599), "text": "think big picture.", "key": "big picture.", "idx": "01 / 04", "size": 150, "motion": "rise"},
    {"a": E(22.127), "b": E(23.908) + .15, "text": "four types.", "key": "four", "idx": "02 / 04", "size": 190, "motion": "cut"},
    {"a": E(65.512), "b": E(67.212), "text": "so much easier.", "key": "easier.", "idx": "03 / 04", "size": 190, "motion": "cut"},
]
HAND = {"a": E(69.053), "b": E(75.435) + .15, "words": ["know", "your", "goals", "first."]}
SPLIT = {"a": E(24.188), "b": E(55.502) + .2, "lit": [E(25.869), E(33.833), E(42.056), E(50.6)]}
NOTE = {"in": E(86.598), "out": E(89.519) + .3}
PROMPT = {"in": .32, "out": 4.25}
CAL = {"a": E(114.539), "fill": 1.2}
CAL["b"] = TOTAL + 1
FULL = [(c["a"], c["b"]) for c in CARDS] + [(HAND["a"], HAND["b"]), (SPLIT["a"], SPLIT["b"]), (CAL["a"], CAL["b"])]
KEYS = {"struggling", "match", "education", "entertainment", "truth"}

# Tom captions: 1 to 2 kept words, lowercase, broken at punctuation, never over a card or the split
caps, cur = [], []
kw = [dict(w, t=E(w["start"]), te=E(w["end"])) for w in words if kept(w)]
for w in kw:
    cur.append(w)
    if len(cur) == 2 or w["word"][-1] in ",.?!" or len(" ".join(x["word"] for x in cur)) > 12:
        caps.append(cur); cur = []
if cur:
    caps.append(cur)
CAPS = []
for i, c in enumerate(caps):
    a = c[0]["t"]
    nxt = caps[i + 1][0]["t"] if i + 1 < len(caps) else TOTAL
    b = nxt if nxt - c[-1]["te"] < .6 else c[-1]["te"] + .25
    for fa, fb in FULL:
        if fa - .01 <= a < fb:
            a = None; break
        if a < fa < b:
            b = fa
    if a is None:
        continue
    txt = " ".join(x["word"] for x in c).lower().strip(",.?!").replace("val ", "vale ")
    key = next((x["word"].lower().strip(",.?!") for x in c if x["word"].lower().strip(",.?!") in KEYS), "")
    CAPS.append([r(a), r(b), txt, key])

EV = {"caps": CAPS, "cards": [{k: (r(v) if isinstance(v, float) else v) for k, v in c.items()} for c in CARDS],
      "hand": {**HAND, "a": r(HAND["a"]), "b": r(HAND["b"])}, "split": {"a": r(SPLIT["a"]), "b": r(SPLIT["b"]), "lit": [r(x) for x in SPLIT["lit"]]},
      "note": {k: r(v) for k, v in NOTE.items()}, "prompt": PROMPT, "cal": {k: r(v) for k, v in CAL.items()}, "total": r(TOTAL)}
(OUT / "timeline.json").write_text(json.dumps(EV, indent=1))

# ------------------------------------------------------------------ 1. base
if not (OUT / "base.mp4").exists():
    fc = []
    for i, p in enumerate(pieces):
        fc.append(f"[0:v]trim=start_frame={p['inFrame']}:end_frame={p['outFrame']},setpts=PTS-STARTPTS[v{i}]")
        fc.append(f"[0:a]atrim=start={p['inFrame'] / FPS}:end={p['outFrame'] / FPS},asetpts=PTS-STARTPTS[a{i}]")
    fc.append("".join(f"[v{i}][a{i}]" for i in range(len(pieces))) + f"concat=n={len(pieces)}:v=1:a=1[vc][ac]")
    s, e = round(SPLIT["a"] * FPS), round(SPLIT["b"] * FPS)
    fc.append(f"[vc]lut3d=file='{LUT}',split[sa][sb];[sb]crop=1080:1220:0:0,pad=1080:1920:0:700:black[sh];"
              f"[sa][sh]overlay=0:0:enable='between(n,{s},{e - 1})'[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(MASTER), "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[ac]",
                    "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", "-fps_mode", "passthrough",
                    "-c:a", "aac", "-b:a", "320k", str(OUT / "base.mp4")], check=True)
    print("base done", flush=True)

# ------------------------------------------------------------------ 2. overlay timeline
CAVEAT = (ROOT / "brand/fonts/Caveat[wght].ttf").as_uri()
SUN = '<svg viewBox="-20 -20 40 40" class="sun"><circle r="5.2"/>' + "".join(
    f'<path d="M0 -8.5 Q 2.2 -12 0 -17 Q -2.2 -12 0 -8.5" transform="rotate({a})"/>' for a in range(0, 360, 30)) + "</svg>"
ARROW = '<svg viewBox="0 0 24 24"><path d="M12 19V5M5 12l7-7 7 7"/></svg>'
PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face { font-family:"Caveat"; src:url("__CAVEAT__"); }
* { margin:0; padding:0; box-sizing:border-box; }
html,body { width:1080px; height:1920px; overflow:hidden; background:transparent; font-family:"Helvetica Neue"; -webkit-font-smoothing:antialiased; }
.layer { position:absolute; inset:0; display:none; }
.mono { background:#151413; color:#F2EEE8; }
.lab { position:absolute; top:268px; left:110px; font:500 22px/1 "Helvetica Neue"; letter-spacing:.24em; text-transform:uppercase; color:rgba(242,238,232,.55); }
.idx { position:absolute; top:268px; right:110px; font:500 22px/1 "Helvetica Neue"; letter-spacing:.18em; color:rgba(242,238,232,.55); font-variant-numeric:tabular-nums; }
.rule { position:absolute; top:312px; left:110px; right:110px; height:1px; background:rgba(242,238,232,.22); transform-origin:left; }
.sun { position:absolute; left:508px; top:1520px; width:64px; height:64px; fill:#E6D8BC; }
.stage { position:absolute; left:110px; right:110px; top:0; bottom:0; display:flex; align-items:center; justify-content:center; text-align:center; }
.t { font-weight:700; line-height:1.02; letter-spacing:-.035em; } .t .w { display:inline-block; } .acc { color:#E6D8BC; }
#cap { position:absolute; left:90px; right:90px; top:1060px; text-align:center; font:700 96px/1.02 "Helvetica Neue"; letter-spacing:-.025em; color:#fff;
       text-shadow:0 0 36px rgba(0,0,0,.6), 0 4px 14px rgba(0,0,0,.55), 0 1px 3px rgba(0,0,0,.5); }
.ui { position:absolute; left:110px; right:110px; top:245px; border-radius:30px; padding:26px 32px; background:#F4F0EC; color:#151413;
      box-shadow:0 24px 60px rgba(0,0,0,.28), 0 2px 6px rgba(0,0,0,.12); display:none; }
.ui .l { font:500 20px/1 "Helvetica Neue"; letter-spacing:.22em; text-transform:uppercase; opacity:.55; margin-bottom:18px; }
.row { display:flex; align-items:center; gap:22px; }
.ui .x { flex:1; font:500 40px/1.25 "Helvetica Neue"; white-space:nowrap; overflow:hidden; }
.btn { width:68px; height:68px; border-radius:50%; display:grid; place-items:center; background:#151413; color:#F4F0EC; flex:none; }
.btn svg { width:28px; height:28px; fill:none; stroke:currentColor; stroke-width:3; stroke-linecap:round; stroke-linejoin:round; }
.av { width:72px; height:72px; border-radius:50%; display:grid; place-items:center; font:700 30px/1 "Helvetica Neue"; background:#151413; color:#F4F0EC; flex:none; }
#panel { position:absolute; left:0; right:0; top:0; height:940px; }
.li { position:absolute; left:110px; right:110px; display:flex; gap:40px; align-items:baseline; padding:26px 0; border-top:1px solid rgba(242,238,232,.18); }
.li i { font:500 26px/1 "Helvetica Neue"; letter-spacing:.18em; color:rgba(242,238,232,.55); font-style:normal; width:60px; }
.li b { font:700 72px/1 "Helvetica Neue"; letter-spacing:-.03em; }
.paper { background:#F3F1EC; }
.ink { position:absolute; left:150px; top:700px; font:600 128px/1.08 "Caveat"; color:#2B3E6E; } .ink span { display:inline-block; }
.by { position:absolute; left:156px; top:1020px; font:500 26px/1 "Helvetica Neue"; letter-spacing:.2em; text-transform:uppercase; color:rgba(43,62,110,.6); }
.cal { display:grid; grid-template-columns:repeat(7, 100px); gap:20px; } .cell { height:100px; border-radius:14px; border:1px solid rgba(242,238,232,.22); }
.cell.off { border-color:transparent; } .cell.on { background:#E6D8BC; border-color:#E6D8BC; }
.dows { width:820px; display:grid; grid-template-columns:repeat(7, 100px); gap:20px; } .dows span { font:500 22px/1 "Helvetica Neue"; letter-spacing:.2em; color:rgba(242,238,232,.55); text-align:center; }
canvas.grain { position:absolute; inset:0; width:1080px; height:1920px; mix-blend-mode:overlay; pointer-events:none; display:none; }
</style></head><body>
<div id="split" class="layer"><div id="panel" class="mono"><div class="lab">Four types</div><div class="idx" id="sidx">01 / 04</div><div class="rule"></div>
__ROWS__</div></div>
<div id="card" class="layer mono"><div class="lab">Vale Studio</div><div class="idx" id="cidx"></div><div class="rule" id="crule"></div>__SUN__<div class="stage"><div class="t" id="ct"></div></div></div>
<div id="hand" class="layer paper"><div class="ink" id="ink"></div><div class="by" id="by">— vale studio</div></div>
<div id="cal" class="layer mono"><div class="lab">Vale Studio</div><div class="idx">04 / 04</div><div class="rule"></div>__SUN__
  <div class="stage" style="flex-direction:column;gap:34px"><div style="width:820px;display:flex;align-items:baseline;gap:26px">
  <span id="cn" style="font:700 150px/1 'Helvetica Neue';letter-spacing:-.04em;font-variant-numeric:tabular-nums">0</span>
  <span style="font:500 30px/1.2 'Helvetica Neue';color:rgba(242,238,232,.55)">posts this month</span></div>
  <div class="dows">__DOWS__</div><div class="cal" id="grid">__CELLS__</div></div></div>
<canvas class="grain" id="grain" width="360" height="640"></canvas>
<div id="cap"></div>
<div class="ui" id="prompt"><div class="l">Vale Studio</div><div class="row"><div class="x" id="px"></div><div class="btn">__ARROW__</div></div></div>
<div class="ui" id="note"><div class="row"><div class="av">J</div><div style="flex:1"><div class="row" style="justify-content:space-between">
  <b style="font:700 34px/1.1 'Helvetica Neue'">New application</b><span style="font:500 24px/1 'Helvetica Neue';opacity:.55">now</span></div>
  <div style="font:500 32px/1.3 'Helvetica Neue';margin-top:8px;opacity:.8">Jess: love your team's videos. Are you hiring?</div></div></div></div>
<script>
const EV = __EV__;
window.DURATION = EV.total;
const $ = (q) => document.querySelector(q), $$ = (q) => [...document.querySelectorAll(q)];
const cl = (x) => Math.max(0, Math.min(1, x)), ease = (k) => 1 - Math.pow(1 - cl(k), 3);
const G = $("#grain"), gx = G.getContext("2d");
function grain(f, op) { G.style.display = op ? "block" : "none"; if (!op) return; G.style.opacity = op;
  let s = (f * 9301 + 49297) % 233280; const img = gx.createImageData(360, 640), d = img.data;
  for (let i = 0; i < d.length; i += 4) { s = (s * 9301 + 49297) % 233280; const v = (s / 233280) * 255; d[i] = d[i+1] = d[i+2] = v; d[i+3] = 255; } gx.putImageData(img, 0, 0); }
const show = (el, on) => { el.style.display = on ? "block" : "none"; return on; };
const keyed = (text, key) => key && text.includes(key) ? text.replace(key, `<span class="acc">${key}</span>`) : text;
const cells = () => $$(".cell:not(.off)");

window.seek = (t) => {
  let full = false, gr = 0;
  // split panel
  const S = EV.split, inS = t >= S.a && t < S.b;
  if (show($("#split"), inS)) {
    full = true;
    let lit = -1; S.lit.forEach((x, i) => { if (t >= x) lit = i; });
    $("#sidx").textContent = `0${Math.max(1, lit + 1)} / 04`;
    $$(".li").forEach((el, i) => { const k = ease((t - S.a - i * .09) / .52); el.style.opacity = k; el.style.transform = `translateY(${28 * (1 - k)}px)`;
      const on = i === lit, f = on ? ease((t - S.lit[i]) / .25) : 0; el.querySelector("b").style.color = `rgba(242,238,232,${.3 + .7 * f})`; });
  }
  // cards
  const C = EV.cards.find((c) => t >= c.a && t < c.b);
  if (show($("#card"), !!C)) {
    full = true; gr = .2;
    $("#cidx").textContent = C.idx; const ct = $("#ct"); ct.style.fontSize = C.size + "px";
    if (ct.dataset.k !== C.text) { ct.dataset.k = C.text; ct.innerHTML = C.text.split(" ").map((w) => `<span class="w">${keyed(w, C.key.includes(w) ? w : "")}</span>`).join(" "); }
    $$("#ct .w").forEach((w, i) => { const k = C.motion === "rise" ? ease((t - C.a - i * .09) / .52) : 1; w.style.opacity = k; w.style.transform = `translateY(${28 * (1 - k)}px)`; });
    $("#crule").style.transform = `scaleX(${ease((t - C.a) / .6)})`;
  }
  // handwritten card
  const H = EV.hand, inH = t >= H.a && t < H.b;
  if (show($("#hand"), inH)) {
    full = true; gr = .16;
    if (!$("#ink").children.length) $("#ink").innerHTML = "<span>know</span> <span>your</span><br><span>goals</span> <span>first.</span>";
    $$("#ink span").forEach((w, i) => w.style.opacity = ease((t - H.a - .35 - i * .11) / .26));
    $("#by").style.opacity = ease((t - H.a - 1.5) / .5);
  }
  // calendar
  const K = EV.cal, inK = t >= K.a;
  if (show($("#cal"), inK)) {
    full = true; gr = .2; let n = 0;
    cells().forEach((c, i) => { const on = t >= K.a + .25 + i * (K.fill / 30); c.classList.toggle("on", on); if (on) n++; });
    $("#cn").textContent = n;
  }
  grain(Math.round(t * 30), gr);
  // captions (never over a full-screen layer)
  const cap = EV.caps.find((c) => t >= c[0] && t < c[1]);
  if (show($("#cap"), !!cap && !full)) $("#cap").innerHTML = keyed(cap[2], cap[3]);
  // prompt bar
  const P = EV.prompt;
  if (show($("#prompt"), t >= P.in && t < P.out + .3)) {
    const k = ease((t - P.in) / .48), o = t > P.out ? 1 - cl((t - P.out) / .3) : 1;
    $("#prompt").style.opacity = k * o; $("#prompt").style.transform = `translateY(${-36 * (1 - k)}px)`;
    const full_ = "what should I film this week?", q = cl((t - .55) / .9);
    $("#px").textContent = full_.slice(0, Math.round(full_.length * q)) + (q < 1 && Math.floor(t * 4) % 2 ? "|" : "");
  }
  // notification
  const N = EV.note;
  if (show($("#note"), t >= N.in && t < N.out + .3 && !full)) {
    const k = ease((t - N.in) / .48), o = t > N.out ? 1 - cl((t - N.out) / .3) : 1;
    $("#note").style.opacity = k * o; $("#note").style.transform = `translateY(${-36 * (1 - k)}px)`;
  }
};
window.seek(0);
</script></body></html>"""
TYPES = ["education", "entertainment", "inspirational", "trending"]
rows = "".join(f'<div class="li" style="top:{370 + i * 130}px"><i>{i + 1:02d}</i><b>{w}</b></div>' for i, w in enumerate(TYPES))
cells = "".join(f'<div class="cell{" off" if i < 2 or i > 31 else ""}"></div>' for i in range(35))
html = (PAGE.replace("__CAVEAT__", CAVEAT).replace("__ROWS__", rows).replace("__SUN__", SUN).replace("__ARROW__", ARROW)
        .replace("__DOWS__", "".join(f"<span>{d}</span>" for d in "MTWTFSS")).replace("__CELLS__", cells).replace("__EV__", json.dumps(EV)))
(OUT / "timeline.html").write_text(html)
if "--skip-frames" not in sys.argv and "--page-only" not in sys.argv:
    subprocess.run(["node", str(ROOT / "style-lab/render/render.mjs"), str(OUT / "timeline.html"), str(OUT / "frames"), "30", "1080", "1920", "--transparent"], check=True)
if "--page-only" in sys.argv:
    sys.exit(0)

# ------------------------------------------------------------------ 3. sounds (kept Style Lab sounds, synthesised)
ns = {"__file__": str(ROOT / "style-lab/round3/gen2.py")}  # helpers resolve round1 from here; audio lands in style-lab/round3/audio
exec((ROOT / "style-lab/round2/gen2.py").read_text().split("# ------------------------------------------------------------------ Fixes (the Maybes)")[0], ns)
SR, mix, write_wav, s_click, s_filmclick, s_whoosh = ns["SR"], ns["mix"], ns["write_wav"], ns["s_click"], ns["s_filmclick"], ns["s_whoosh"]
pk = lambda s: int(np.argmax(np.abs(s))) / SR
click = s_click(); breath, boff = s_whoosh(.7, 250, 900, 400, .8, 2.6); whoosh, woff = s_whoosh(.32, 500, 1400, 700, 1.2, 1.6); film = s_filmclick()
ev = [(click, .8, pk(click), .8), (breath, CARDS[0]["a"], boff, 1), (film, CARDS[1]["a"], 0, 1)]
ev += [(click, x, pk(click), .8) for x in SPLIT["lit"]]
ev += [(whoosh, CARDS[2]["a"], woff, 1), (click, HAND["a"] + .35, pk(click), .7), (click, NOTE["in"] + .45, pk(click), .8),
       (breath, CAL["a"] + .7, boff, .8), (click, CAL["a"] + .25 + CAL["fill"], pk(click), .8)]
write_wav("IMG_9225_v1_sfx", mix(TOTAL + .5, ev, gain_db=-9))

# ------------------------------------------------------------------ 4. final
final = HERE / "v1" / "IMG_9225_vale_v1.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(OUT / "base.mp4"), "-framerate", "30", "-i", str(OUT / "frames/%05d.png"),
                "-i", str(ROOT / "style-lab/round3/audio/IMG_9225_v1_sfx.wav"), "-filter_complex",
                "[0:v][1:v]overlay=0:0:eof_action=pass,format=yuv420p[v];[0:a][2:a]amix=inputs=2:duration=first:normalize=0,"
                "volume=-0.95dB,alimiter=limit=0.84:level=false[a]",
                "-map", "[v]", "-map", "[a]", "-fps_mode", "cfr", "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high", "-c:a", "aac", "-b:a", "256k",
                "-movflags", "+faststart", str(final)], check=True)
print("final:", final, flush=True)
