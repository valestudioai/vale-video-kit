"""Snap transcript/cuts.json to the footage frame grid and print the timeline placement."""
import json, sys
from fractions import Fraction
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
FPS = Fraction(24000, 1001)
segs = json.loads((ROOT / "transcript/cuts.json").read_text())["segments"]
rec, out = 0, []
for s in segs:
    a, b = round(Fraction(s["start"]) * FPS), round(Fraction(s["end"]) * FPS)
    out.append({"inFrame": a, "outFrame": b, "frames": b - a, "recFrame": rec,
                "sourceIn": float(a / FPS), "sourceOut": float(b / FPS), "time": float(rec / FPS)})
    rec += b - a
json.dump({"fps": "24000/1001", "totalFrames": rec, "totalSeconds": float(rec / FPS), "pieces": out},
          sys.stdout, indent=2)
