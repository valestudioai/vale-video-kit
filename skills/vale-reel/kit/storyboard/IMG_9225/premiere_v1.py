"""Make storyboard v1 of IMG_9225 editable in Premiere (EDIT.prproj).

Steps (run in order):
  render   graphics-only and captions-only versions of v1/render/timeline.html -> transparent PNG frames (in parallel)
  encode   one QuickTime Animation (alpha) clip per graphic (prompt, cards, split panel, handwritten card,
           notification, calendar) and one full-length captions layer -> v1/premiere/
  plan     v1/premiere/premiere_plan.json: V1 speaker pieces from renders/IMG_9225_master.mov (mid-frame source
           times, split at the split-screen bounds, Motion position y 1660 during the split), V2 graphics,
           V3 captions, A2 sound effects

Usage: python3 storyboard/IMG_9225/premiere_v1.py render|encode|plan
"""
import json
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
R = HERE / "v1" / "render"
P = HERE / "v1" / "premiere"
P.mkdir(parents=True, exist_ok=True)
os.environ["PATH"] = str(Path.home() / ".local/bin") + os.pathsep + os.environ["PATH"]
FPS = 30
EV = json.loads((R / "timeline.json").read_text())
NFR = round(EV["total"] * FPS)
f = lambda s: round(s * FPS)

# graphic windows on V2, in timeline frames [start, end)
GFX = [("01_prompt", f(EV["prompt"]["in"]), f(EV["prompt"]["out"] + .3))]
GFX += [(f"0{i + 2}_card_{c['text'].split()[-1].strip('.')}", f(c["a"]), f(c["b"])) for i, c in enumerate(EV["cards"][:1])]
GFX += [("03_card_types", f(EV["cards"][1]["a"]), f(EV["cards"][1]["b"])),
        ("04_split_four_types", f(EV["split"]["a"]), f(EV["split"]["b"])),
        ("05_card_easier", f(EV["cards"][2]["a"]), f(EV["cards"][2]["b"])),
        ("06_hand_goals", f(EV["hand"]["a"]), f(EV["hand"]["b"])),
        ("07_note_application", f(EV["note"]["in"]), f(EV["note"]["out"] + .3)),
        ("08_calendar", f(EV["cal"]["a"]), NFR)]

step = sys.argv[1]
if step == "render":
    src = (R / "timeline.html").read_text()
    variants = {"gfx": "#cap { visibility:hidden !important; }",
                "caps": ".layer, .ui, canvas.grain { visibility:hidden !important; }"}
    procs = []
    for name, css in variants.items():
        page = R / f"timeline_{name}.html"
        page.write_text(src.replace("</style>", css + "\n</style>", 1))
        procs.append(subprocess.Popen(["node", str(ROOT / "style-lab/render/render.mjs"), str(page), str(R / f"frames_{name}"),
                                       "30", "1080", "1920", "--transparent"]))
    for p in procs:
        p.wait()
        assert p.returncode == 0
    print("rendered gfx and caps layers")

elif step == "encode":
    def anim(frames_dir, start, n, out):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-start_number", str(start), "-i", str(frames_dir / "%05d.png"),
                        "-frames:v", str(n), "-c:v", "qtrle", "-pix_fmt", "argb", str(out)], check=True)
    def opaque(frames_dir, start, n, out):  # full-screen cards: no alpha needed, and grain bloats Animation files
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-start_number", str(start), "-i", str(frames_dir / "%05d.png"),
                        "-frames:v", str(n), "-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le", str(out)], check=True)
    for name, a, b in GFX:
        full = any(k in name for k in ("card", "hand", "calendar"))
        (opaque if full else anim)(R / "frames_gfx", a, b - a, P / f"{name}.mov")
        print(name, b - a, "frames")
    anim(R / "frames_caps", 0, NFR, P / "09_captions.mov")
    print("captions", NFR, "frames")

elif step == "plan":
    pieces = json.loads((ROOT / "transcript/IMG_9225/frames.json").read_text())["pieces"]
    sa, sb = f(EV["split"]["a"]), f(EV["split"]["b"])
    v1, motion = [], []
    for p in pieces:
        s, e = p["recFrame"], p["recFrame"] + p["frames"]
        cuts = sorted({s, e} | {x for x in (sa, sb) if s < x < e})
        for a, b in zip(cuts, cuts[1:]):
            si = p["inFrame"] + (a - s)
            v1.append({"time": a / FPS, "sourceInPoint": (si + .5) / FPS, "sourceOutPoint": (si + (b - a) + .5) / FPS,
                       "startFrame": a, "endFrame": b})
            motion.append({"position": {"x": 540, "y": 1660}} if sa <= a < sb else None)
    overlays = [{"file": str(P / f"{n}.mov"), "trackIndex": 1, "time": a / FPS, "frames": b - a} for n, a, b in GFX]
    overlays.append({"file": str(P / "09_captions.mov"), "trackIndex": 2, "time": 0.0, "frames": NFR})
    plan = {"fps": FPS, "timelineFrames": NFR, "master": str(ROOT / "renders/IMG_9225_master.mov"),
            "sfx": str(ROOT / "style-lab/round3/audio/IMG_9225_v1_sfx.wav"), "lut": str(ROOT / "presets/look/Vale_Warm_Natural.cube"),
            "v1": v1, "motion": motion, "overlays": overlays}
    (P / "premiere_plan.json").write_text(json.dumps(plan, indent=1))
    print(len(v1), "V1 pieces,", sum(1 for m in motion if m), "in the split,", len(overlays), "overlay clips")
