"""Round 1 sound options. Each sound is synthesised from scratch (no library, no downloads): filtered noise, tones
and transients, trimmed with short fades and peak-limited to -1.5 dBFS. Each lands at 0.8 s on a 2.4 s animation
made for it. Writes audio/<id>.wav, pages/<id>.html and appends the sound section to manifest.json.
"""
import json
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
(HERE / "audio").mkdir(exist_ok=True)
SR, DUR, HIT = 48000, 2.4, 0.8
rng = np.random.default_rng(7)


def env(n, a, d):
    """Attack/decay envelope, seconds."""
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)


def onepole(x, fc, hp=False):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(x); s = 0.0
    for i, v in enumerate(x):
        s = (1 - a) * v + a * s; y[i] = s
    return x - y if hp else y


def bandsweep(x, f0, f1, q=2.0):
    """State-variable band-pass with the centre frequency sweeping f0 -> f1 (log)."""
    n = len(x); y = np.zeros(n); low = band = 0.0
    fs = np.exp(np.linspace(np.log(f0), np.log(f1), n))
    for i in range(n):
        f = 2 * np.sin(np.pi * fs[i] / SR)
        low += f * band; high = x[i] - low - band / q; band += f * high; y[i] = band
    return y


def place(sig, peak_at):
    """Put sig into a DUR-long buffer so its loudest sample lands at HIT."""
    out = np.zeros(int(SR * DUR))
    k = int(np.argmax(np.abs(sig))) if peak_at is None else int(peak_at * SR)
    start = int(HIT * SR) - k
    s0, d0 = max(0, start), max(0, -start)
    m = min(len(out) - s0, len(sig) - d0)
    out[s0:s0 + m] = sig[d0:d0 + m]
    return out


def finish(sig):
    fade_in, fade_out = int(.003 * SR), int(.04 * SR)
    nz = np.nonzero(np.abs(sig) > 1e-5)[0]
    if len(nz):
        a, b = nz[0], nz[-1]
        sig[a:a + fade_in] *= np.linspace(0, 1, fade_in)
        sig[max(a, b - fade_out):b] *= np.linspace(1, 0, b - max(a, b - fade_out))
    return sig / np.max(np.abs(sig)) * 10 ** (-1.5 / 20)


def write(name, sig):
    data = (np.clip(sig, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(HERE / "audio" / f"{name}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())


def n(sec):
    return int(SR * sec)


# 1. Soft click: a tiny noise tick plus a 3.1 kHz ping that dies in 30 ms
t = np.arange(n(.12)) / SR
click = onepole(rng.standard_normal(n(.12)), 6000) * env(n(.12), .0005, .004) * .9 + np.sin(2 * np.pi * 3100 * t) * env(n(.12), .0005, .03) * .35
write("r1-e1", finish(place(click, None)))

# 2. Soft whoosh: noise through a band-pass sweeping 300 Hz -> 2.4 kHz -> 600 Hz, swelling into the hit
w_n = n(.55)
noise = rng.standard_normal(w_n)
sweep = np.concatenate([bandsweep(noise[: w_n * 2 // 3], 300, 2400, 1.6), bandsweep(noise[w_n * 2 // 3:], 2400, 600, 1.6)])
shape = np.sin(np.linspace(0, np.pi, w_n)) ** 2.2
write("r1-e2", finish(place(sweep * shape, .55 * 2 / 3)))

# 3. Paper slide: soft low-passed noise with a little grain flutter, ending on a quiet tap
p_n = n(.38)
paper = onepole(onepole(rng.standard_normal(p_n), 2600), 2600, hp=False)
paper *= np.linspace(.2, 1, p_n) ** 1.5 * (1 + .25 * np.sin(np.arange(p_n) / SR * 2 * np.pi * 37))
tap = onepole(rng.standard_normal(n(.06)), 1800) * env(n(.06), .0005, .012) * 1.6
write("r1-e3", finish(place(np.concatenate([paper, tap]), p_n / SR)))

# 4. Punchy hit: a 52 Hz body dropping to 44 Hz, a noise crack on top, soft saturation
h_n = n(.7)
th = np.arange(h_n) / SR
body = np.sin(2 * np.pi * np.cumsum(np.linspace(52, 44, h_n)) / SR) * env(h_n, .002, .22)
crack = onepole(rng.standard_normal(h_n), 3500) * env(h_n, .0005, .018) * .7
hit = np.tanh((body + crack) * 2.2)
write("r1-e4", finish(place(hit, None)))

# 5. Film click: a camera-shutter double transient with a short mechanical rattle
f_n = n(.18)
tick = lambda d: onepole(rng.standard_normal(f_n), 5200, hp=True) * env(f_n, .0003, d)
sh = tick(.006) + np.roll(tick(.01) * .8, n(.045)) + np.roll(onepole(rng.standard_normal(f_n), 2500) * env(f_n, .001, .03) * .25, n(.05))
write("r1-e5", finish(place(sh, .045)))

# ---------- the animations they play on (monochrome card, everything lands at 0.8 s) ----------
import gen  # noqa: E402  (reuses the page template and palette)

CSS = gen.TEXT_CSS.format(w=700, s=150, ls="-.035em", extra="")
S = [
    ("r1-e1", "Soft click", "A short tick with a high ping, on a word cutting in. For card cuts and small UI moments.",
     '<div class="t">better.</div>',
     'anim($(".t"), [{opacity:0},{opacity:0,offset:.999},{opacity:1}], {duration:800, easing:"steps(1,end)"});'),
    ("r1-e2", "Soft whoosh", "A filtered air sweep that peaks as a cream panel wipes across. For transitions and fast moves.",
     '<div class="t">better.</div><div class="wipe"></div>',
     'anim($(".wipe"), [{transform:"translateX(-110%)"},{transform:"translateX(110%)"}], {duration:520, delay:440, easing:"cubic-bezier(.6,0,.3,1)"});'
     'anim($(".t"), [{opacity:0},{opacity:0,offset:.999},{opacity:1}], {duration:720, easing:"steps(1,end)"});'),
    ("r1-e3", "Paper slide", "Soft paper friction with a quiet tap as a card lands. For cards and notes sliding in.",
     '<div class="paper"><span>better.</span></div>',
     'anim($(".paper"), [{transform:"translateY(1100px) rotate(4deg)"},{transform:"translateY(0) rotate(-1.5deg)"}], {duration:420, delay:380, easing:"cubic-bezier(.2,.75,.25,1)"});'),
    ("r1-e4", "Punchy hit", "A deep 50 Hz thump with a crack on top, on a big word slamming in with a 3-frame shake. For big moments only.",
     '<div class="t big">BETTER</div>',
     'anim($(".t"), [{opacity:0, transform:"scale(1.35)"},{opacity:0, transform:"scale(1.35)", offset:.82},{opacity:1, transform:"scale(1)"}], {duration:800, easing:"cubic-bezier(.7,0,1,.4)"});'
     'window.onFrame = (t) => { const f = Math.round((t - .8) * 30), k = [10, -7, 4][f] || 0; document.body.style.transform = (f >= 0 && f < 3) ? `translate(${k}px, ${-k*.6}px)` : "none"; };'),
    ("r1-e5", "Film click", "A shutter-style double click with a flash frame as the picture snaps into focus. Analog, filmic.",
     '<div class="t">better.</div><div class="flash"></div>',
     'anim($(".t"), [{opacity:0, filter:"blur(18px)"},{opacity:0, filter:"blur(18px)", offset:.999},{opacity:1, filter:"blur(0)"}], {duration:800, easing:"steps(1,end)"});'
     'anim($(".flash"), [{opacity:0},{opacity:0,offset:.98},{opacity:.85},{opacity:0}], {duration:900, easing:"linear"});'),
]
EXTRA = (" .wipe { position:absolute; top:0; bottom:0; left:0; width:100%; background:#E6D8BC; transform:translateX(-110%); }"
         " .paper { position:absolute; left:150px; right:150px; top:690px; height:540px; border-radius:22px; background:#EEE5D3;"
         " box-shadow:0 30px 60px rgba(0,0,0,.45); display:grid; place-items:center; }"
         ' .paper span { font:700 130px/1 "Helvetica Neue"; letter-spacing:-.035em; color:#171513; }'
         ' .big { font-stretch:condensed; font-weight:900; font-size:260px; }'
         " .flash { position:absolute; inset:0; background:#fff; opacity:0; }")
manifest = json.loads((HERE / "manifest.json").read_text())
manifest["sections"] = [s for s in manifest["sections"] if s["id"] != "r1-sounds"]
manifest["cards"] = [c for c in manifest["cards"] if c["section"] != "r1-sounds"]
manifest["sections"].append({"id": "r1-sounds", "name": "Sounds",
                             "use": "Each sound plays on a short animation of the thing it's for, landing at 0.8 s. Open one full size to hear it. Synthesised from scratch in code (no AI sound generator is connected yet).",
                             "order": 5})
for i, (cid, label, desc, body, js) in enumerate(S):
    gen.page(cid, "mono", f'<div class="card"></div>{gen.DETAILS}<div class="stage">{body}</div>', css=CSS + EXTRA, js=js, dur=DUR)
    manifest["cards"].append({"id": cid, "section": "r1-sounds", "label": label, "desc": desc, "order": i + 1,
                              "kind": "video", "sound": True, "source": "Synthesised in code by Claude / " + cid + ".wav"})
(HERE / "manifest.json").write_text(json.dumps(manifest, indent=2))
print("sounds:", len(S))
