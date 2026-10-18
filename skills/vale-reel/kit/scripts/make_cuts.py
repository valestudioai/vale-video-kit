"""Build a tight cut list from a clip's word timings.

Keeps every word except the ranges in DROP, removes pauses longer than MAX_GAP, and pads each kept
piece by 0.08 s before and 0.12 s after (splitting the gap when two pieces sit closer than that).
Writes transcript/<clip>/cuts.json and transcript/<clip>/frames.json (frame-snapped at the clip's rate).

Usage: python3 scripts/make_cuts.py IMG_9225
"""
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
clip = sys.argv[1]
TDIR = ROOT / "transcript" / clip
src = next((ROOT / "raw").glob(f"{clip}.*"))
MAX_GAP, PRE, POST = 0.25, 0.08, 0.12

# Word ranges (raw seconds, inclusive of the words that start inside them) to drop: false starts, stutters.
DROP = {
    "IMG_9225": [
        (6.80, 7.10, "hesitation 'that' in 'I think that it's'"),
        (17.65, 17.80, "stutter 'is, is'"),
        (56.65, 57.55, "abandoned start 'and i think if you can' (restarted at 59.9)"),
    ],
}.get(clip, [])
FIXES = {"Val": "Vale"}

words = [w for w in json.loads((TDIR / "words.json").read_text())["words"] if w["start"] is not None]
for w in words:
    w["word"] = FIXES.get(w["word"], w["word"])
keep = [w for w in words if not any(a <= w["start"] < b for a, b, _ in DROP)]

# Group consecutive kept words into runs; a dropped word or a long pause ends a run.
runs, cur = [], [keep[0]]
for prev, w in zip(keep, keep[1:]):
    dropped_between = any(prev["end"] <= x["start"] < w["start"] and x not in keep for x in words)
    if w["start"] - prev["end"] > MAX_GAP or dropped_between:
        runs.append(cur)
        cur = [w]
    else:
        cur.append(w)
runs.append(cur)

segs = [{"start": r[0]["start"] - PRE, "end": r[-1]["end"] + POST, "text": " ".join(w["word"] for w in r)} for r in runs]
for a, b in zip(segs, segs[1:]):  # never overlap: split the gap
    if a["end"] > b["start"]:
        mid = (a["end"] + b["start"]) / 2
        a["end"] = b["start"] = mid
segs[0]["start"] = max(0.0, segs[0]["start"])

rate = subprocess.run([str(Path.home() / ".local/bin/ffprobe"), "-v", "error", "-select_streams", "v:0", "-show_entries",
                       "stream=r_frame_rate", "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout.strip().strip(",").splitlines()[0].strip(",")
FPS = Fraction(rate)
(TDIR / "cuts.json").write_text(json.dumps({"source": src.name, "dropped": [d[2] for d in DROP],
                                            "segments": [{k: (round(v, 3) if k != "text" else v) for k, v in s.items()} for s in segs]}, indent=2))
rec, pieces = 0, []
for s in segs:
    a, b = round(Fraction(s["start"]) * FPS), round(Fraction(s["end"]) * FPS)
    pieces.append({"inFrame": a, "outFrame": b, "frames": b - a, "recFrame": rec,
                   "sourceIn": float(a / FPS), "sourceOut": float(b / FPS), "time": float(rec / FPS)})
    rec += b - a
(TDIR / "frames.json").write_text(json.dumps({"fps": rate, "totalFrames": rec, "totalSeconds": float(rec / FPS), "pieces": pieces}, indent=2))
raw_len = words[-1]["end"]
print(f"{len(segs)} pieces, {float(rec / FPS):.2f} s cut (from {raw_len:.2f} s of speech), {rate} fps")
for s in segs:
    print(f"  {s['start']:7.2f}-{s['end']:7.2f}  {s['text']}")
