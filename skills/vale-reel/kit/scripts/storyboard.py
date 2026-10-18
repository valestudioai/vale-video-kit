"""Storyboard a clip before anything is rendered (the justyn.ai way: see what Claude is thinking, then change it in a sentence).

Claude writes storyboard/<clip>/plan.json: the direction, the look, and one entry per beat in raw seconds
(shot type, what happens, labelled rows such as sound or captions, and the mock frames to draw).
This script does the mechanical part:
  - maps each beat's raw seconds to edit time through transcript/<clip>/frames.json (the approved cut)
  - pulls the spoken words for each beat from transcript/<clip>/words.json
  - grabs a graded raw frame per beat and renders each mock frame (HTML templates in Vale's locked style,
    captured with style-lab/render/render.mjs, composited over the raw frame with ffmpeg)
  - writes storyboard/<clip>/v<N>/board.json and 360x640 JPEGs for the Storyboard page

Usage:
  python3 scripts/storyboard.py IMG_9225              # build version N (next free number)
  python3 scripts/storyboard.py IMG_9225 --writes N   # after uploading v<N>/frames, make db_writes.json from v<N>/assets.json
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.environ["PATH"] = str(Path.home() / ".local/bin") + os.pathsep + os.environ["PATH"]
clip = sys.argv[1]
SB = ROOT / "storyboard" / clip
plan = json.loads((SB / "plan.json").read_text())
words = json.loads((ROOT / "transcript" / clip / "words.json").read_text())["words"]
pieces = json.loads((ROOT / "transcript" / clip / "frames.json").read_text())["pieces"]
src = next((ROOT / "raw").glob(f"{clip}.*"))
LUT = ROOT / "presets/look/Vale_Warm_Natural.cube"
RENDER = ROOT / "style-lab/render/render.mjs"
CAVEAT = (ROOT / "brand/fonts/Caveat[wght].ttf").as_uri()


def edit_time(t):
    """Raw seconds -> seconds in the cut. A time inside a removed gap snaps to the next kept piece."""
    for p in pieces:
        if t < p["sourceIn"]:
            return p["time"]
        if t <= p["sourceOut"]:
            return p["time"] + t - p["sourceIn"]
    last = pieces[-1]
    return last["time"] + last["sourceOut"] - last["sourceIn"]


def tc(s):
    return f"{int(s // 60):02d}:{s % 60:04.1f}"


def kept(w):
    m = (w["start"] + w["end"]) / 2
    return any(p["sourceIn"] <= m <= p["sourceOut"] for p in pieces)


def words_in(a, b):
    """Spoken words in the beat that survive the cut (stutters and false starts removed)."""
    return " ".join(w["word"] for w in words if a - 0.05 <= w["start"] < b and kept(w)).strip()


# ------------------------------------------------------------------ mock frame templates (Vale locked style)
CSS = """@font-face { font-family:"Caveat"; src:url("%s"); }
* { margin:0; padding:0; box-sizing:border-box; }
html,body { width:1080px; height:1920px; overflow:hidden; background:transparent; font-family:"Helvetica Neue"; -webkit-font-smoothing:antialiased; }
.full { position:absolute; inset:0; background:#151413; color:#F2EEE8; }
.lab { position:absolute; top:268px; left:110px; font:500 22px/1 "Helvetica Neue"; letter-spacing:.24em; text-transform:uppercase; color:rgba(242,238,232,.55); }
.idx { position:absolute; top:268px; right:110px; font:500 22px/1 "Helvetica Neue"; letter-spacing:.18em; color:rgba(242,238,232,.55); }
.rule { position:absolute; top:312px; left:110px; right:110px; height:1px; background:rgba(242,238,232,.22); }
.sun { position:absolute; left:508px; top:1520px; width:64px; height:64px; fill:#E6D8BC; }
.stage { position:absolute; left:110px; right:110px; top:0; bottom:0; display:flex; align-items:center; justify-content:center; text-align:center; }
.t { font:700 150px/1.02 "Helvetica Neue"; letter-spacing:-.035em; } .t.big { font-size:190px; }
.acc { color:#E6D8BC; }
.cap { position:absolute; left:90px; right:90px; top:1060px; text-align:center; font:700 96px/1.02 "Helvetica Neue"; letter-spacing:-.025em; color:#fff;
       text-shadow:0 0 36px rgba(0,0,0,.6), 0 4px 14px rgba(0,0,0,.55), 0 1px 3px rgba(0,0,0,.5); }
.ui { position:absolute; left:110px; right:110px; top:245px; border-radius:30px; padding:26px 32px; background:#F4F0EC; color:#151413; box-shadow:0 24px 60px rgba(0,0,0,.28); }
.ui .l { font:500 20px/1 "Helvetica Neue"; letter-spacing:.22em; text-transform:uppercase; opacity:.55; margin-bottom:18px; }
.row { display:flex; align-items:center; gap:22px; }
.ui .x { flex:1; font:500 40px/1.25 "Helvetica Neue"; white-space:nowrap; overflow:hidden; }
.btn { width:68px; height:68px; border-radius:50%%; display:grid; place-items:center; background:#151413; color:#F4F0EC; flex:none; }
.btn svg { width:28px; height:28px; fill:none; stroke:currentColor; stroke-width:3; stroke-linecap:round; stroke-linejoin:round; }
.av { width:72px; height:72px; border-radius:50%%; display:grid; place-items:center; font:700 30px/1 "Helvetica Neue"; background:#151413; color:#F4F0EC; flex:none; }
.panel { position:absolute; left:0; right:0; top:0; height:940px; background:#151413; color:#F2EEE8; }
.li { position:absolute; left:110px; right:110px; display:flex; gap:40px; align-items:baseline; padding:26px 0; border-top:1px solid rgba(242,238,232,.18); }
.li i { font:500 26px/1 "Helvetica Neue"; letter-spacing:.18em; color:rgba(242,238,232,.55); font-style:normal; width:60px; }
.li b { font:700 72px/1 "Helvetica Neue"; letter-spacing:-.03em; color:rgba(242,238,232,.3); } .li.on b { color:#F2EEE8; }
.paper { position:absolute; inset:0; background:#F3F1EC; }
.ink { position:absolute; left:150px; top:700px; font:600 128px/1.08 "Caveat"; color:#2B3E6E; }
.by { position:absolute; left:156px; top:1020px; font:500 26px/1 "Helvetica Neue"; letter-spacing:.2em; text-transform:uppercase; color:rgba(43,62,110,.6); }
.cal { display:grid; grid-template-columns:repeat(7, 100px); gap:20px; } .cell { height:100px; border-radius:14px; background:#E6D8BC; } .cell.off { background:none; }
""" % CAVEAT
SUN = '<svg viewBox="-20 -20 40 40" class="sun"><circle r="5.2"/>' + "".join(
    f'<path d="M0 -8.5 Q 2.2 -12 0 -17 Q -2.2 -12 0 -8.5" transform="rotate({a})"/>' for a in range(0, 360, 30)) + "</svg>"
ARROW = '<svg viewBox="0 0 24 24"><path d="M12 19V5M5 12l7-7 7 7"/></svg>'
TYPES = ["education", "entertainment", "inspirational", "trending"]


def keyed(text, key):
    if key and key in text:
        a, b = text.split(key, 1)
        return f'{a}<span class="acc">{key}</span>{b}'
    return text


def mock_body(f):
    k = f["kind"]
    if k == "card":
        return (f'<div class="full"><div class="lab">Vale Studio</div><div class="idx">{f.get("idx", "")}</div><div class="rule"></div>{SUN}'
                f'<div class="stage"><div class="t{" big" if f.get("big") else ""}">{keyed(f["text"], f.get("key"))}</div></div></div>')
    if k == "caption":
        return f'<div class="cap">{keyed(f["text"], f.get("key"))}</div>'
    if k == "prompt":
        return f'<div class="ui"><div class="l">Vale Studio</div><div class="row"><div class="x">{f["text"]}</div><div class="btn">{ARROW}</div></div></div>'
    if k == "note":
        return (f'<div class="ui"><div class="row"><div class="av">{f["av"]}</div><div style="flex:1"><div class="row" style="justify-content:space-between">'
                f'<b style="font:700 34px/1.1 \'Helvetica Neue\'">{f["title"]}</b><span style="font:500 24px/1 \'Helvetica Neue\';opacity:.55">now</span></div>'
                f'<div style="font:500 32px/1.3 \'Helvetica Neue\';margin-top:8px;opacity:.8">{f["body"]}</div></div></div></div>')
    if k == "split":
        rows = "".join(f'<div class="li{" on" if i == f["lit"] else ""}" style="top:{370 + i * 130}px"><i>{i + 1:02d}</i><b>{w}</b></div>' for i, w in enumerate(TYPES))
        return f'<div class="panel"><div class="lab">Four types</div><div class="idx">{f["lit"] + 1:02d} / 04</div><div class="rule"></div>{rows}</div>'
    if k == "hand":
        return '<div class="paper"><div class="ink">' + "<br>".join(f["lines"]) + '</div><div class="by">— vale studio</div></div>'
    if k == "calendar":
        cells = "".join(f'<div class="cell{" off" if i < 2 or i > 31 else ""}"></div>' for i in range(35))
        return (f'<div class="full"><div class="lab">Vale Studio</div><div class="idx">04 / 04</div><div class="rule"></div>{SUN}'
                f'<div class="stage" style="flex-direction:column;gap:40px"><div style="width:820px;display:flex;align-items:baseline;gap:26px">'
                f'<span style="font:700 150px/1 \'Helvetica Neue\';letter-spacing:-.04em">30</span><span style="font:500 30px/1.2 \'Helvetica Neue\';color:rgba(242,238,232,.55)">posts this month</span></div>'
                f'<div class="cal">{cells}</div></div></div>')
    raise ValueError(k)


FULL = {"card", "hand", "calendar"}


def run(*a):
    subprocess.run([str(x) for x in a], check=True)


def raw_frame(t, out):
    run("ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", src, "-frames:v", "1",
        "-vf", f"lut3d='{LUT}',scale=1080:1920", out)


# ------------------------------------------------------------------ --writes: Style Lab database rows for the Storyboard page
if "--writes" in sys.argv:
    n = int(sys.argv[sys.argv.index("--writes") + 1])
    V = SB / f"v{n}"
    board = json.loads((V / "board.json").read_text())
    assets = json.loads((V / "assets.json").read_text())  # {"b01_raw.jpg": "<asset id>", ...}
    writes = [{"op": "set", "collection": "board", "doc_id": "current", "data": {k: v for k, v in board.items() if k != "beats"}}]
    for b in board["beats"]:
        d = dict(b)
        d["version"] = n
        d["frames"] = [{"label": fr["label"], "asset": assets[fr["file"]]} for fr in b["frames"]]
        writes.append({"op": "set", "collection": "beats", "doc_id": f"v{n}-{b['id']}", "data": d})
    (V / "db_writes.json").write_text(json.dumps(writes))
    print(len(writes), "writes ->", V / "db_writes.json")
    sys.exit(0)

# ------------------------------------------------------------------ build a version
n = 1
while (SB / f"v{n}").exists():
    n += 1
V = SB / f"v{n}"
FR, TMP = V / "frames", V / "tmp"
FR.mkdir(parents=True)
TMP.mkdir()
beats = []
for i, b in enumerate(plan["beats"]):
    bid = f"b{i + 1:02d}"
    es, ee = edit_time(b["start"]), edit_time(b["end"])
    frames = []
    mid = (b["start"] + b["end"]) / 2
    raw_png = TMP / f"{bid}_raw.png"
    raw_frame(b["frames"][0].get("at", mid) if b["frames"] else mid, raw_png)
    run("ffmpeg", "-v", "error", "-y", "-i", raw_png, "-vf", "scale=360:640:flags=lanczos", "-q:v", "4", FR / f"{bid}_raw.jpg")
    frames.append({"file": f"{bid}_raw.jpg", "label": f"raw {tc(b['start'])}"})
    for j, f in enumerate(b["frames"]):
        page = TMP / f"{bid}_m{j}.html"
        page.write_text(f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{mock_body(f)}"
                        "<script>window.DURATION = 1/30; window.seek = () => {};</script></body></html>")
        shot = TMP / f"{bid}_m{j}"
        run("node", RENDER, page, shot, 30, 1080, 1920, "--transparent")
        ov = shot / "00000.png"
        out = FR / f"{bid}_m{j}.jpg"
        if f["kind"] in FULL:
            run("ffmpeg", "-v", "error", "-y", "-i", ov, "-vf", "scale=360:640:flags=lanczos", "-q:v", "4", out)
        else:
            under = raw_png
            if "at" in f and f["at"] != (b["frames"][0].get("at") if b["frames"] else None):
                under = TMP / f"{bid}_m{j}_raw.png"
                raw_frame(f["at"], under)
            base = "[0:v]crop=1080:1220:0:0,pad=1080:1920:0:700:black[b]" if f["kind"] == "split" else "[0:v]null[b]"
            run("ffmpeg", "-v", "error", "-y", "-i", under, "-i", ov, "-filter_complex",
                f"{base};[b][1:v]overlay=0:0,scale=360:640:flags=lanczos", "-q:v", "4", out)
        frames.append({"file": out.name, "label": f["kind"]})
    beats.append({"id": bid, "order": i + 1, "shot": b["shot"], "rawStart": b["start"], "rawEnd": b["end"],
                  "start": round(es, 2), "end": round(ee, 2), "range": f"{tc(es)}–{tc(ee)}", "dur": round(ee - es, 1),
                  "say": words_in(b["start"], b["end"]), "do": b["do"], "rows": b.get("rows", {}), "frames": frames})
shutil.rmtree(TMP)
total = pieces[-1]["time"] + pieces[-1]["sourceOut"] - pieces[-1]["sourceIn"]
board = {"clip": clip, "title": plan["title"], "direction": plan["direction"], "look": plan["look"], "version": n,
         "beatCount": len(beats), "duration": round(total, 1), "status": "draft", "beats": beats}
(V / "board.json").write_text(json.dumps(board, indent=1))
print(f"v{n}: {len(beats)} beats, {sum(len(b['frames']) for b in beats)} frames -> {V}")
