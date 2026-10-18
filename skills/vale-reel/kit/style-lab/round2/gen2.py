"""Round 2 option pages, audio and manifest for Style Lab.

Built from round 1's notes: fixes for the Maybes, monochrome pushed further with dusty blue, split screens on real
footage, and animations on a plain background. Reuses round 1's page template and palette.
"""
import json
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
CAVEAT_URI = (HERE.resolve().parents[1] / "brand/fonts/Caveat[wght].ttf").as_uri()
R1 = HERE.parent / "round1"
for d in ("pages", "split_pages", "audio"):
    (HERE / d).mkdir(exist_ok=True)

# Round 1's template without running its round (everything above its card list)
ns = {"__file__": str(R1 / "gen.py")}
exec((R1 / "gen.py").read_text().split("cards, sections = [], []")[0], ns)
ns["PAGES"] = HERE / "pages"
page, PAL, DETAILS, TEXT_CSS, words_html = ns["page"], ns["PAL"], ns["DETAILS"], ns["TEXT_CSS"], ns["words_html"]
HARD_CUT_JS = ns["HARD_CUT_JS"]
WORDS = ["better", "than", "it", "looks."]
CAVEAT = ' @font-face { font-family:"Caveat"; src:url("' + CAVEAT_URI + '"); }'

# Extra palettes: monochrome pushed with dusty blue
PAL["mono_blueword"] = {**PAL["mono"], "acc": "#9DB0DA"}
PAL["blueblack"] = {**PAL["mono"], "bg": "#121722"}
PAL["light_blueword"] = {"bg": "#E4E4DF", "fg": "#151413", "acc": "#3C5182", "sub": "rgba(21,20,19,.55)", "line": "rgba(21,20,19,.22)", "grain": .14}
PAL["mono_bluedetail"] = {**PAL["mono"], "sub": "rgba(157,176,218,.85)", "line": "rgba(157,176,218,.45)"}

sections, cards = [], []


def section(sid, name, use, order):
    sections.append({"id": sid, "name": name, "use": use, "order": order})


def card(cid, sec, label, desc, order, **kw):
    cards.append({"id": cid, "section": sec, "label": label, "desc": desc, "order": order, "kind": "video", **kw})


# ------------------------------------------------------------------ audio (synthesised from scratch)
SR = 48000
rng = np.random.default_rng(11)


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)


def onepole(x, fc, hp=False):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    for i, v in enumerate(x):
        s = (1 - a) * v + a * s; y[i] = s
    return x - y if hp else y


def bandsweep(x, f0, f1, q):
    n = len(x); y = np.zeros(n); low = band = 0.0
    fs = np.exp(np.linspace(np.log(f0), np.log(f1), n))
    for i in range(n):
        f = 2 * np.sin(np.pi * fs[i] / SR); low += f * band; high = x[i] - low - band / q; band += f * high; y[i] = band
    return y


def N(s):
    return int(SR * s)


def s_click():
    t = np.arange(N(.12)) / SR
    return onepole(rng.standard_normal(N(.12)), 6000) * env(N(.12), .0005, .004) * .9 + np.sin(2 * np.pi * 3100 * t) * env(N(.12), .0005, .03) * .35


def s_paper():
    n = N(.34)
    p = onepole(onepole(rng.standard_normal(n), 2600), 2600) * np.linspace(.2, 1, n) ** 1.5 * (1 + .25 * np.sin(np.arange(n) / SR * 2 * np.pi * 37))
    tap = onepole(rng.standard_normal(N(.06)), 1800) * env(N(.06), .0005, .012) * 1.6
    return np.concatenate([p, tap]), n / SR  # sound, offset of the landing


def s_filmclick():
    n = N(.18)
    tick = lambda d: onepole(rng.standard_normal(n), 5200, hp=True) * env(n, .0003, d)
    return tick(.006) + np.roll(tick(.01) * .8, N(.045)) + np.roll(onepole(rng.standard_normal(n), 2500) * env(n, .001, .03) * .25, N(.05))


def s_whoosh(dur, f0, fpk, f1, q, power):
    n = N(dur); x = rng.standard_normal(n); k = int(n * .62)
    y = np.concatenate([bandsweep(x[:k], f0, fpk, q), bandsweep(x[k:], fpk, f1, q)])
    return y * np.sin(np.linspace(0, np.pi, n)) ** power, k / SR


def s_softthud():
    n = N(.45)
    body = np.sin(2 * np.pi * np.cumsum(np.linspace(78, 66, n)) / SR) * env(n, .004, .09)
    air = onepole(rng.standard_normal(n), 900) * env(n, .002, .03) * .5
    return np.tanh((body + air) * 1.2)


def mix(dur, events, gain_db=-1.5):
    """events: [(sound, at_seconds, offset_in_sound_seconds, level)] -> normalised buffer."""
    out = np.zeros(N(dur))
    for snd, at, off, lvl in events:
        s0 = N(at - off)
        a, b = max(0, s0), min(len(out), s0 + len(snd))
        out[a:b] += snd[a - s0:b - s0] * lvl
    if np.max(np.abs(out)) > 0:
        out = out / np.max(np.abs(out)) * 10 ** (gain_db / 20)
    return out


def write_wav(name, sig):
    nz = np.nonzero(np.abs(sig) > 1e-5)[0]
    if len(nz):
        a, b = nz[0], nz[-1]; fi, fo = N(.003), N(.04)
        sig[a:a + fi] *= np.linspace(0, 1, fi); sig[max(a, b - fo):b] *= np.linspace(1, 0, b - max(a, b - fo))
    with wave.open(str(HERE / "audio" / f"{name}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(sig, -1, 1) * 32767).astype(np.int16).tobytes())


# ------------------------------------------------------------------ Fixes (the Maybes)
section("r2-fix", "Fixes from round 1",
        "Your Maybes, changed the way your notes said, plus a softer answer to \"punchier on big moments\" since the punchy hit was dropped.", 1)
A_CSS = TEXT_CSS.format(w=700, s=150, ls="-.035em", extra="") + " .acc { color: var(--acc); }"
# Repeated stack inside the Instagram safe zone: widest row fits 820 px, block sits between y 360 and 1300
STACK_CSS = (".t { font-stretch:condensed; font-weight:800; text-transform:uppercase; line-height:1.02; letter-spacing:-.005em; white-space:nowrap; }"
             + "".join(f" .r{i} {{ font-size:{30 + i * 11}px; opacity:{0.35 + i * 0.1:.2f}; }}" for i in range(7)))
page("r2-f1", "mono", f'<div class="card"></div>{DETAILS}<div class="stage"><div class="t">' + "<br>".join(f'<span class="r{i}">Better than it looks</span>' for i in range(7)) + "</div></div>",
     css=STACK_CSS, js=HARD_CUT_JS)
card("r2-f1", "r2-fix", "Repeated stack, inside the safe zone",
     "Fixes \"not in safe zone\": the rows grow to a 96px max so the widest fits inside the Reels safe area, with nothing under the buttons. Turn on Safe zones to check.", 1)

SNAPPY = (B_CSS := TEXT_CSS.format(w=700, s=150, ls="-.035em", extra="") + " .acc { color: var(--acc); } .m { display:inline-block; overflow:hidden; vertical-align:top; padding-bottom:.08em; }")
SNAPPY_HTML = " ".join(f'<span class="m"><span class="w{" acc" if i == 0 else ""}">{w}</span></span>' for i, w in enumerate(WORDS))
SNAPPY_JS = '$$(".m > .w").forEach((w, i) => anim(w, [{transform:"translateY(105%)"},{transform:"none"}], {duration:240, delay:620 + i*60, easing:"cubic-bezier(.7,0,.2,1)"}));'
page("r2-f2", "mono", f'<div class="card"></div>{DETAILS}<div class="stage"><div class="t">{SNAPPY_HTML}</div></div>', css=SNAPPY, js=SNAPPY_JS)
w, off = s_whoosh(.32, 500, 1400, 700, 1.2, 1.6)
write_wav("r2-f2", mix(2.6, [(w, .8, off, 1)]))
card("r2-f2", "r2-fix", "Whoosh, shorter and softer",
     "The whoosh cut to 320 ms and pulled down to a 1.4 kHz peak so it sits under the voice. Now on your kept snappy mask, peaking as the words land.", 2,
     sound=True, source="Synthesised in code by Claude / r2-f2.wav")

SMOOTH_JS = '$$(".w").forEach((w, i) => anim(w, [{opacity:0, transform:"translateY(28px)"},{opacity:1, transform:"none"}], {duration:520, delay:560 + i*90, easing:"cubic-bezier(.2,.8,.2,1)"}));'
page("r2-f3", "mono", f'<div class="card"></div>{DETAILS}<div class="stage"><div class="t">{words_html(WORDS, True)}</div></div>', css=A_CSS, js=SMOOTH_JS)
w, off = s_whoosh(.7, 250, 900, 400, .8, 2.6)
write_wav("r2-f3", mix(2.6, [(w, .8, off, 1)]))
card("r2-f3", "r2-fix", "Whoosh, a breath of air",
     "A longer, very low and soft air sweep (700 ms, 900 Hz peak), more felt than heard. On your kept smooth rise.", 3,
     sound=True, source="Synthesised in code by Claude / r2-f3.wav")

BIG_CSS = A_CSS + " .t { font-size:190px; }"
page("r2-f4", "mono", f'<div class="card"></div>{DETAILS}<div class="stage"><div class="t"><span class="w acc">better.</span></div></div>', css=BIG_CSS,
     js='anim($(".t"), [{opacity:0},{opacity:0,offset:.999},{opacity:1}], {duration:800, easing:"steps(1,end)"});')
write_wav("r2-f4", mix(2.6, [(s_softthud(), .8, .004, 1), (s_paper()[0][-N(.06):], .8, 0, .5)]))
card("r2-f4", "r2-fix", "Big moment, softer",
     "Instead of the dropped punchy hit: a short, round 70 Hz thud with a paper tap, no shake. Weight without noise, for the line that matters.", 4,
     sound=True, source="Synthesised in code by Claude / r2-f4.wav")

# ------------------------------------------------------------------ Colour: monochrome pushed with dusty blue
section("r2-colour", "Colour: monochrome with dusty blue",
        "You kept Monochrome and Dusty blue. Same card, words and hard cut as round 1's monochrome; each option changes one thing to bring the blue in.", 2)
CO = [
    ("mono_blueword", "Blue key word", "Monochrome, but the key word is a light dusty blue (#9DB0DA) instead of logo cream."),
    ("blueblack", "Blue-black ground", "The background shifts from warm off-black to a deep blue-black (#121722). Type and cream word unchanged."),
    ("light_blueword", "Light ground, blue word", "Flipped: pale grey-white ground, off-black type, dusty blue key word (#3C5182)."),
    ("mono_bluedetail", "Blue details only", "Monochrome card, cream key word, but the label, index and hairline turn dusty blue. The blue as a quiet accent."),
]
for i, (pal, label, desc) in enumerate(CO):
    cid = f"r2-a{i + 1}"
    page(cid, pal, f'<div class="card"></div>{DETAILS}<div class="stage"><div class="t">{words_html(WORDS, True)}</div></div>', css=A_CSS, js=HARD_CUT_JS)
    card(cid, "r2-colour", label, desc, i + 1)

# ------------------------------------------------------------------ Split screens on footage
section("r2-split", "Split screen with animation",
        "Your footage below, an animation above (Gannon, Cooperson, RPN). Same clip, same chart, same timing. Each option changes one thing. Open one to hear it.", 3)
CHART_PANEL = """<!doctype html><html><head><meta charset="utf-8"><style>
:root {{ --panel:{panel}; --fg:{fg}; --sub:{sub}; --line:{line}; --stroke:{stroke}; --acc:{acc}; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:1080px; height:1920px; overflow:hidden; background:transparent; font-family:"Helvetica Neue"; -webkit-font-smoothing:antialiased; }}
.panel {{ position:absolute; {panelpos} background:var(--panel); {panelextra} overflow:hidden; }}
.lab {{ position:absolute; left:{px}px; top:{ly}px; font:500 22px/1 "Helvetica Neue"; letter-spacing:.24em; text-transform:uppercase; color:var(--sub); }}
.idx {{ position:absolute; right:{px}px; top:{ly}px; font:500 22px/1 "Helvetica Neue"; letter-spacing:.18em; color:var(--sub); }}
.rule {{ position:absolute; left:{px}px; right:{px}px; top:{ry}px; height:1px; background:var(--line); transform-origin:left; }}
.num {{ position:absolute; left:{px}px; top:{ny}px; font:700 {ns}px/1 "Helvetica Neue"; letter-spacing:-.04em; color:var(--fg); font-variant-numeric:tabular-nums; }}
.cap {{ position:absolute; left:{px}px; top:{cy}px; font:500 30px/1.2 "Helvetica Neue"; color:var(--sub); }}
svg.ch {{ position:absolute; left:{px}px; top:{chy}px; width:{chw}px; height:{chh}px; overflow:visible; }}
.grid line {{ stroke:var(--line); stroke-width:1; }}
.dot {{ fill:var(--acc); }}
</style></head><body>
<div class="panel">{panelinner}
<div class="lab">Posts this month</div><div class="idx">01 / 04</div><div class="rule"></div>
<div class="num" id="num">0</div><div class="cap">from one shoot day</div>
{chart}
</div>
<script>
window.DURATION = 2.9; const A = [];
function anim(el, kf, o) {{ const a = el.animate(kf, {{ fill:"both", ...o }}); a.pause(); A.push(a); return a; }}
const $ = (q) => document.querySelector(q);
const p = document.querySelector("#line"); const L = p ? p.getTotalLength() : 0;
if (p) {{ p.style.strokeDasharray = L; anim(p, [{{strokeDashoffset:L}},{{strokeDashoffset:0}}], {{duration:1300, delay:350, easing:"cubic-bezier(.45,.05,.2,1)"}}); }}
if ($(".dot")) anim($(".dot"), [{{opacity:0, transform:"scale(.2)"}},{{opacity:1, transform:"scale(1)"}}], {{duration:260, delay:1600, easing:"cubic-bezier(.2,.8,.2,1)"}});
anim($(".rule"), [{{transform:"scaleX(0)"}},{{transform:"scaleX(1)"}}], {{duration:600, delay:150, easing:"cubic-bezier(.2,.8,.2,1)"}});
{panelanim}
window.seek = (t) => {{ for (const a of A) a.currentTime = t*1000;
  const k = Math.min(1, Math.max(0, (t - .35) / 1.3)), e = 1 - Math.pow(1 - k, 3);
  document.getElementById("num").textContent = Math.round(30 * e); }};
window.seek(0);
</script></body></html>"""
PTS = [(0, 300), (90, 285), (180, 290), (270, 240), (360, 225), (450, 170), (540, 150), (630, 95), (720, 60), (810, 20)]


def chart_svg(w, h, stroke, dotr=11):
    sx, sy = w / 810, h / 300
    d = "M" + " L".join(f"{x * sx:.1f} {y * sy:.1f}" for x, y in PTS)
    grid = "".join(f'<line x1="0" x2="{w}" y1="{h * k / 3:.1f}" y2="{h * k / 3:.1f}"/>' for k in range(4))
    lx, ly = PTS[-1][0] * sx, PTS[-1][1] * sy
    return (f'<svg class="ch" viewBox="0 0 {w} {h}"><g class="grid">{grid}</g>'
            f'<path id="line" d="{d}" fill="none" stroke="{stroke}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle class="dot" cx="{lx:.1f}" cy="{ly:.1f}" r="{dotr}" style="transform-origin:{lx:.1f}px {ly:.1f}px"/></svg>')


SPLIT = {"panel": "#151413", "fg": "#F2EEE8", "sub": "rgba(242,238,232,.55)", "line": "rgba(242,238,232,.18)", "stroke": "#F2EEE8", "acc": "#E6D8BC"}
SPLIT_LIGHT = {"panel": "#E4E4DF", "fg": "#151413", "sub": "rgba(21,20,19,.55)", "line": "rgba(21,20,19,.16)", "stroke": "#3C5182", "acc": "#3C5182"}
HARD = dict(panelpos="left:0; right:0; top:0; height:940px;", panelextra="", px=110, ly=268, ry=312, ny=370, ns=150, cy=530,
            chy=610, chw=860, chh=260, panelinner="", panelanim="")
SPLITS = [
    ("r2-s1", "Monochrome panel, chart", "Hard split at 940px. Warm off-black panel; the line chart draws itself while the number counts to 30. Line draw borrows the stroke-dash technique from the ideas library (ik-builds-585923).",
     dict(**SPLIT, **HARD, chart=chart_svg(860, 260, SPLIT["stroke"])), "shift"),
    ("r2-s2", "Light panel, dusty blue chart", "The same split and chart on a pale grey-white panel with a dusty blue line.",
     dict(**SPLIT_LIGHT, **HARD, chart=chart_svg(860, 260, SPLIT_LIGHT["stroke"])), "shift"),
    ("r2-s3", "Floating card", "Instead of a hard split, the chart sits on a rounded card floating over a softened, dimmed copy of the shot. Gannon-style.",
     dict(**SPLIT, **{**HARD, "panelpos": "left:90px; right:90px; top:220px; height:700px;", "panelextra": "border-radius:30px; box-shadow:0 40px 80px rgba(0,0,0,.45);",
                      "px": 60, "ly": 56, "ry": 98, "ny": 150, "cy": 310, "chy": 400, "chw": 780, "chh": 220,
                      "panelanim": 'anim($(".panel"), [{opacity:0, transform:"translateY(40px)"},{opacity:1, transform:"none"}], {duration:520, delay:0, easing:"cubic-bezier(.2,.8,.2,1)"});'},
          chart=chart_svg(780, 220, SPLIT["stroke"])), "blurbg"),
    ("r2-s4", "Monochrome panel, number only", "The same hard split, but just the number counting up to 30, huge, with no chart. Simpler.",
     dict(**SPLIT, **{**HARD, "ny": 400, "ns": 420, "cy": 830}, chart=""), "shift"),
]
for i, (cid, label, desc, kw, mode) in enumerate(SPLITS):
    (HERE / "split_pages" / f"{cid}.html").write_text(CHART_PANEL.format(**kw))
    card(cid, "r2-split", label, desc, i + 1, sound=True, mode=mode)

# ------------------------------------------------------------------ Animations on a plain background
section("r2-anim", "Animations on a plain background",
        "Full-screen explainer moments on the monochrome card, all moving with your kept smooth ease and carrying your kept sounds. Same story in each: one shoot day becomes a month of posts. Open one to hear it.", 4)
ANIM_BASE_CSS = A_CSS + CAVEAT + (
    " .sm { font:500 30px/1.2 'Helvetica Neue'; color:var(--sub); }"
    " .big { font:700 150px/1 'Helvetica Neue'; letter-spacing:-.04em; font-variant-numeric:tabular-nums; }"
    " .col { display:flex; flex-direction:column; gap:28px; align-items:center; }"
    " .tile { width:820px; padding:44px 50px; border-radius:28px; background:#1E1C1B; box-shadow:0 30px 60px rgba(0,0,0,.4); border:1px solid rgba(242,238,232,.08); display:flex; justify-content:space-between; align-items:baseline; }"
    " .tile b { font:700 96px/1 'Helvetica Neue'; letter-spacing:-.04em; } .tile span { font:500 32px/1 'Helvetica Neue'; color:var(--sub); }"
    " .row { width:860px; display:flex; gap:40px; align-items:baseline; padding:30px 0; border-top:1px solid var(--line); position:relative; }"
    " .row i { font:500 26px/1 'Helvetica Neue'; letter-spacing:.18em; color:var(--sub); font-style:normal; width:60px; }"
    " .row b { font:700 72px/1 'Helvetica Neue'; letter-spacing:-.03em; color:rgba(242,238,232,.3); }"
    " .row.on b { color:var(--fg); } .note { font:600 80px/1 'Caveat'; color:var(--acc); }"
)
EASE = "cubic-bezier(.2,.8,.2,1)"
click, paper, film = s_click(), s_paper(), s_filmclick()
ANIMS = [
    ("r2-m1", "Chart draws on", "A line chart draws itself as the number counts to 30, then a soft click as the end dot lands. Line draw: stroke-dash (ik-builds-585923).",
     '<div class="col" style="align-items:flex-start;width:860px"><div class="sm">Posts this month</div><div class="big" id="n">0</div>'
     + chart_svg(860, 300, "#F2EEE8").replace('class="ch"', 'class="ch" style="position:relative;left:0;top:0;width:860px;height:300px;margin-top:40px"').replace('class="dot"', 'class="dot" fill="#E6D8BC"') + '<div class="sm">from one shoot day</div></div>',
     'const p = $("#line"), L = p.getTotalLength(); p.style.strokeDasharray = L;'
     'anim(p, [{strokeDashoffset:L},{strokeDashoffset:0}], {duration:1400, delay:400, easing:"cubic-bezier(.45,.05,.2,1)"});'
     'anim($(".dot"), [{opacity:0, transform:"scale(.2)"},{opacity:1, transform:"scale(1)"}], {duration:260, delay:1750, easing:"' + EASE + '"});'
     'window.onFrame = (t) => { const k = Math.min(1, Math.max(0, (t - .4) / 1.4)); $("#n").textContent = Math.round(30 * (1 - Math.pow(1 - k, 3))); };',
     [(click, 1.80, None, 1)]),
    ("r2-m2", "Stat cards stack in", "Three cards slide up and land one after another, each with a soft paper slide: 1 day, 30 posts, 0 stress.",
     '<div class="col">' + "".join(f'<div class="tile"><b>{b}</b><span>{s}</span></div>' for b, s in [("1", "shoot day"), ("30", "posts"), ("0", "stress")]) + "</div>",
     '$$(".tile").forEach((el, i) => anim(el, [{opacity:0, transform:"translateY(120px)"},{opacity:1, transform:"none"}], {duration:520, delay:400 + i*420, easing:"' + EASE + '"}));',
     [(paper[0], .92 + i * .42, paper[1], .9) for i in range(3)]),
    ("r2-m3", "Handwritten note draws on", "The statement cuts in, then a handwritten note writes itself on with a hand-drawn arrow, with a film click as it starts.",
     '<div class="col"><div class="t">one day<br>of filming.</div><div class="note" id="nt">= a month of posts</div>'
     '<svg width="300" height="120" viewBox="0 0 300 120" style="position:absolute;left:600px;top:1010px;overflow:visible"><path id="ar" d="M20 100 C 90 110, 170 80, 230 20 M230 20 L200 26 M230 20 L226 52" stroke="#E6D8BC" stroke-width="6" fill="none" stroke-linecap="round"/></svg></div>',
     'anim($(".t"), [{opacity:0},{opacity:0,offset:.999},{opacity:1}], {duration:350, easing:"steps(1,end)"});'
     'anim($("#nt"), [{clipPath:"inset(0 100% 0 0)"},{clipPath:"inset(0 0 0 0)"}], {duration:900, delay:900, easing:"cubic-bezier(.4,0,.2,1)"});'
     'const a = $("#ar"), L = a.getTotalLength(); a.style.strokeDasharray = L; anim(a, [{strokeDashoffset:L},{strokeDashoffset:0}], {duration:600, delay:1750, easing:"' + EASE + '"});',
     [(film, .9, .0, .8)]),
    ("r2-m4", "Numbered list builds", "A four-step list with hairlines drawing in; each step lights up in turn with a soft click: plan, film, edit, post.",
     '<div class="col" style="gap:0">' + "".join(f'<div class="row"><i>{i + 1:02d}</i><b>{w}</b></div>' for i, w in enumerate(["plan", "film", "edit", "post"])) + "</div>",
     '$$(".row").forEach((el, i) => anim(el, [{opacity:0, transform:"translateY(24px)"},{opacity:1, transform:"none"}], {duration:420, delay:300 + i*120, easing:"' + EASE + '"}));'
     'window.onFrame = (t) => $$(".row").forEach((el, i) => el.classList.toggle("on", t >= 1.0 + i*.45));',
     [(click, 1.0 + i * .45, None, .9) for i in range(4)]),
]
for i, (cid, label, desc, body, js, events) in enumerate(ANIMS):
    page(cid, "mono", f'<div class="card"></div>{DETAILS}<div class="stage">{body}</div>', css=ANIM_BASE_CSS, js=js, dur=3.2)
    ev = []
    for snd, at, off, lvl in events:
        if off is None:
            off = int(np.argmax(np.abs(snd))) / SR
        ev.append((snd, at, off, lvl))
    write_wav(cid, mix(3.2, ev))
    card(cid, "r2-anim", label, desc, i + 1, sound=True, source="Synthesised in code by Claude / " + cid + ".wav")

(HERE / "manifest.json").write_text(json.dumps({"sections": sections, "cards": cards}, indent=2))
print(len(cards), "cards")
