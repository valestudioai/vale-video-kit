"""Print the audio offset of file B relative to file A in milliseconds (positive = B is late)."""
import subprocess, sys
from pathlib import Path
import numpy as np
FF = str(Path.home() / ".local/bin/ffmpeg")
def pcm(f, sr=16000):
    b = subprocess.run([FF, "-v", "error", "-i", f, "-vn", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(b, np.int16).astype(np.float32)
a, b = pcm(sys.argv[1]), pcm(sys.argv[2])
n = min(len(a), len(b)); a, b = a[:n], b[:n]
k = int(np.argmax(np.correlate(b[:n], a[: n - 2000][1000:-1000], "valid"))) - 1000 if False else None
lags = range(-1600, 1601)
best = max(lags, key=lambda L: float(np.dot(a[max(0, -L): n - max(0, L)], b[max(0, L): n - max(0, -L)])))
print(f"{best / 16:.2f}")
