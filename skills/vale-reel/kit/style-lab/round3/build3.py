"""Render round 3: every page in manifest.json -> out/<id>_full.mp4 (with sound) and out/<id>_preview.mp4 (540x960, muted).
Usage: python3 build3.py [id ...]   (no ids = all)
"""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
os.chdir(HERE)
os.environ["PATH"] = str(Path.home() / ".local/bin") + ":" + os.environ["PATH"]
SRC = "../round2/footage/img9225_6455.mp4"
SHIFT = 700
(HERE / "out").mkdir(exist_ok=True)
cards = json.loads(Path("manifest.json").read_text())["cards"]
only = set(sys.argv[1:])


def run(*a):
    subprocess.run(a, check=True)


for c in cards:
    cid, mode = c["id"], c["mode"]
    if only and cid not in only:
        continue
    page, frames = f"pages/{cid}.html", f"frames/{cid}"
    if mode in ("card", "full"):
        run("node", "../render/render.mjs", page, frames, "30")
    else:
        run("node", "../render/render.mjs", page, frames, "30", "1080", "1920", "--transparent")
    full = f"out/{cid}_full.mp4"
    enc = ["-c:v", "libx264", "-preset", "slow", "-crf", "17", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", full]
    if mode == "card":
        wav = Path(f"audio/{cid}.wav")
        if wav.exists():
            run("ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", f"{frames}/%05d.png", "-i", str(wav), "-map", "0:v", "-map", "1:a", "-shortest",
                "-vf", "format=yuv420p", *enc)
        else:
            run("ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", f"{frames}/%05d.png", "-vf", "format=yuv420p", "-an", *enc[:6], "-movflags", "+faststart", full)
    else:
        if mode == "full":
            v = "[1:v]format=yuv420p[v]"
        elif mode == "overlay":
            v = "[0:v][1:v]overlay=0:0:shortest=1,format=yuv420p[v]"
        elif mode == "shift":
            v = f"[0:v]crop=1080:{1920 - SHIFT}:0:0,pad=1080:1920:0:{SHIFT}:black[base];[base][1:v]overlay=0:0:shortest=1,format=yuv420p[v]"
        else:  # blurbg
            v = (f"[0:v]split[a][b];[a]scale=1242:2208,crop=1080:1920,boxblur=28:2,eq=brightness=-0.18:saturation=0.7[bg];"
                 f"[b]crop=1080:{1920 - SHIFT}:0:0[sh];[bg][sh]overlay=0:{SHIFT}[base];[base][1:v]overlay=0:0:shortest=1,format=yuv420p[v]")
        voice = "[0:a]" + (f"volume=volume=0:enable='gte(t,{c['voicecut']})'," if c.get("voicecut") else "") + "anull[vo]"
        wav = Path(f"audio/{cid}_sfx.wav")
        if wav.exists():
            a = f"{voice};[vo][2:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[a]"
            ins = ["-i", str(wav)]
        else:
            a = f"{voice};[vo]alimiter=limit=0.89[a]"
            ins = []
        run("ffmpeg", "-v", "error", "-y", "-i", SRC, "-framerate", "30", "-i", f"{frames}/%05d.png", *ins,
            "-filter_complex", f"{v};{a}", "-map", "[v]", "-map", "[a]", "-frames:v", "87", *enc)
    run("ffmpeg", "-v", "error", "-y", "-i", full, "-vf", "scale=540:960:flags=lanczos", "-c:v", "libx264", "-preset", "slow", "-crf", "30", "-an",
        "-movflags", "+faststart", f"out/{cid}_preview.mp4")
    print(cid, mode, f"{Path(f'out/{cid}_preview.mp4').stat().st_size // 1024} KB preview, {Path(full).stat().st_size // 1024} KB full", flush=True)
