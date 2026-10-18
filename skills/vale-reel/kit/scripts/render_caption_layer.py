"""Render one plan track (default: the caption track) as a single transparent movie for Premiere.

Usage: ~/.cache/video-editor/whisperx-venv/bin/python scripts/render_caption_layer.py IMG_9225 vale-hybrid [track=4]
Output: renders/<clip>/<style>/captions_layer.mov (QuickTime Animation, RGBA, timeline length, starts at 0).
"""
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
clip, style = sys.argv[1], sys.argv[2]
track = int(sys.argv[3]) if len(sys.argv) > 3 else 4
D = ROOT / "renders" / clip / style
plan = json.loads((D / "placements.json").read_text())
fps = Fraction(plan["fps"])
frames = plan["timelineFrames"]
clips = sorted((c for c in plan["clips"] if c["track"] == track), key=lambda c: c["startFrame"])

inputs = ["-f", "lavfi", "-i", f"color=c=black@0.0:s=1080x1920:r={fps}:d={float(Fraction(frames) / fps)},format=rgba"]
fc, last = [], "0:v"
for k, c in enumerate(clips, start=1):
    inputs += ["-i", str(D / "overlays" / c["file"])]
    fc.append(f"[{last}][{k}:v]overlay=0:0:format=auto:enable='between(n,{c['startFrame']},{c['endFrame'] - 1})'[o{k}]")
    last = f"o{k}"
out = D / "captions_layer.mov"
subprocess.run([str(Path.home() / ".local/bin/ffmpeg"), "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc),
                "-map", f"[{last}]", "-frames:v", str(frames), "-c:v", "qtrle", "-pix_fmt", "argb", str(out)], check=True)
print(f"Wrote {out} ({len(clips)} captions, {frames} frames)")
