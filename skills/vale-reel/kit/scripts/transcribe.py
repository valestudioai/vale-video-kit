"""Transcribe a raw clip with WhisperX (large-v3-turbo from a local folder, CPU int8, word alignment).
Models come from scripts/download_models.sh (resumable curl).

Usage: ~/.cache/video-editor/whisperx-venv/bin/python scripts/transcribe.py raw/BETTER.mp4
Writes transcript/<name>/<name>.wav and transcript/<name>/words.json. Skips if words.json already exists for this clip.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ["PATH"] = str(Path.home() / ".local/bin") + os.pathsep + os.environ["PATH"]

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / sys.argv[1]).resolve()
out_dir = ROOT / "transcript" / src.stem
out_dir.mkdir(parents=True, exist_ok=True)
words_path = out_dir / "words.json"

if words_path.exists() and json.loads(words_path.read_text()).get("source") == src.name:
    print(f"Already transcribed {src.name}; not running again.")
    sys.exit(0)

wav = out_dir / f"{src.stem}.wav"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-map", "0:a:0", "-vn", "-ac", "1", "-ar", "16000",
                "-c:a", "pcm_s16le", str(wav)], check=True)

import whisperx  # noqa: E402

device, compute = "cpu", "int8"
audio = whisperx.load_audio(str(wav))
MODEL_DIR = Path.home() / ".cache/video-editor/models/faster-whisper-large-v3-turbo"
model = whisperx.load_model(str(MODEL_DIR), device, compute_type=compute)
result = model.transcribe(audio, batch_size=8)
lang = result["language"]
align_model, meta = whisperx.load_align_model(language_code=lang, device=device)
aligned = whisperx.align(result["segments"], align_model, meta, audio, device, return_char_alignments=False)

words = []
for seg in aligned["segments"]:
    for w in seg.get("words", []):
        words.append({"word": w["word"], "start": w.get("start"), "end": w.get("end"), "score": w.get("score")})

words_path.write_text(json.dumps({
    "source": src.name,
    "language": lang,
    "model": "large-v3-turbo",
    "segments": [{"start": s["start"], "end": s["end"], "text": s["text"].strip()} for s in aligned["segments"]],
    "words": words,
}, indent=2))
print(f"Wrote {words_path} ({len(words)} words, language {lang})")
