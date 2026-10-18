"""Turn a rendered style plan into Premiere batches.

Reads transcript/<clip>/frames.json and renders/<clip>/<style>/placements.json and writes
renders/<clip>/<style>/premiere_plan.json with:
  v1:       speaker pieces for add_to_timeline_batch, already split at every split-screen and punch-in boundary,
            using mid-frame source times (Premiere's setInPoint rounds down)
  motion:   Motion settings per v1 piece (by index): position/scale for split screen and punch-ins
  overlays: still overlays per Premiere video track (V1 = speaker, V2 = LUT adjustment layer, V3+ = overlays)

Usage: python3 scripts/premiere_plan.py IMG_9225 vale-hybrid
"""
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
clip, style = sys.argv[1], sys.argv[2]
fr = json.loads((ROOT / "transcript" / clip / "frames.json").read_text())
plan = json.loads((ROOT / "renders" / clip / style / "placements.json").read_text())
FPS = Fraction(fr["fps"])
H = 1920

bounds = set()
for a, b in plan["splitRanges"]:
    bounds |= {a, b}
for p in plan["punchRanges"]:
    bounds |= {p[0], p[1]}


def mode_at(f):
    for a, b in plan["splitRanges"]:
        if a <= f < b:
            return {"kind": "split", "position": {"x": 540, "y": 960 + plan["splitShiftPx"]}, "scale": 100}
    for p in plan["punchRanges"]:
        if p[0] <= f < p[1]:
            z, yf = p[2], p[3]
            src_top = (H - H / z) * yf             # source row that lands at the top of frame
            y = (960 - src_top) * z                # position keeps that row at y = 0 with a centre anchor
            return {"kind": "punch", "position": {"x": 540, "y": round(y, 2)}, "scale": round(z * 100, 3)}
    return {"kind": "normal", "position": {"x": 540, "y": 960}, "scale": 100}


v1, motion = [], []
for p in fr["pieces"]:
    s, e = p["recFrame"], p["recFrame"] + p["frames"]
    cuts = sorted({s, e} | {b for b in bounds if s < b < e})
    for a, b in zip(cuts, cuts[1:]):
        src_in = p["inFrame"] + (a - s)
        src_out = src_in + (b - a)
        v1.append({"time": float(Fraction(a) / FPS), "sourceInPoint": float((src_in + Fraction(1, 2)) / FPS),
                   "sourceOutPoint": float((src_out + Fraction(1, 2)) / FPS), "startFrame": a, "endFrame": b})
        motion.append(mode_at(a))

TRACK = {1: 2, 2: 3, 3: 4, 4: 4, 5: 5}  # plan track -> Premiere video track index (0 = V1)
overlays = [{"file": c["file"], "trackIndex": TRACK[c["track"]], "time": float(Fraction(c["startFrame"]) / FPS),
             "frames": c["endFrame"] - c["startFrame"], "startFrame": c["startFrame"], "endFrame": c["endFrame"]}
            for c in plan["clips"]]
out = ROOT / "renders" / clip / style / "premiere_plan.json"
out.write_text(json.dumps({"fps": fr["fps"], "timelineFrames": plan["timelineFrames"], "v1": v1, "motion": motion,
                           "overlays": overlays}, indent=2))
from collections import Counter
print(f"v1 pieces {len(v1)} ({Counter(m['kind'] for m in motion)}), overlays {len(overlays)} "
      f"on tracks {sorted(Counter(o['trackIndex'] for o in overlays).items())} -> {out}")
