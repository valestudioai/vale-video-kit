"""Round 3 option pages, audio and manifest for Style Lab.

Built from round 2's notes (read per card; round 2 wasn't submitted):
  - Ideas kept, effect not: the repeated stack and the handwritten card get new movement (only kept motions).
  - Maybes: light ground with a blue word, the dusty blue stack and the number-only split are fixed or pushed.
  - Big moments: both low hits were dropped, the whooshes were kept, so big moments are tried with whooshes, a film
    click and silence.
  - Keeps pushed further: split screens, plain-background animations, UI cards.
Never brought back: blue inside monochrome, low thuds, B&W timecode, print border, sticker, pill label, glitch,
karaoke captions, Helvetica Medium big type.
Modes (build3.py): card = full page with its own sound; full = full page over the clip's voice; overlay = transparent
page over the clip; shift / blurbg = split screens over the clip.
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
for d in ("pages", "audio"):
    (HERE / d).mkdir(exist_ok=True)

# Round 2's helpers (round 1's page template, palettes, synth and mixer) without running round 2's cards
ns = {"__file__": str(HERE / "gen2.py")}
exec((HERE.parent / "round2" / "gen2.py").read_text().split("# ------------------------------------------------------------------ Fixes (the Maybes)")[0], ns)
page, PAL, DETAILS, TEXT_CSS, words_html = ns["page"], ns["PAL"], ns["DETAILS"], ns["TEXT_CSS"], ns["words_html"]
HARD_CUT_JS, WORDS, CAVEAT = ns["HARD_CUT_JS"], ns["WORDS"], ns["CAVEAT"]
SR, N, mix, write_wav = ns["SR"], ns["N"], ns["mix"], ns["write_wav"]
s_click, s_paper, s_filmclick, s_whoosh = ns["s_click"], ns["s_paper"], ns["s_filmclick"], ns["s_whoosh"]

EASE = "cubic-bezier(.2,.8,.2,1)"
SNAP = "cubic-bezier(.7,0,.2,1)"
SUN = ns["SUN"] if "SUN" in ns else ""
sections, cards = [], []


def section(sid, name, use, order):
    sections.append({"id": sid, "name": name, "use": use, "order": order})


def card(cid, sec, label, desc, order, mode, **kw):
    cards.append({"id": cid, "section": sec, "label": label, "desc": desc, "order": order, "kind": "video", "mode": mode, **kw})


# Kept sounds (round 1 and 2), rebuilt with the same settings
def click():
    c = s_click(); return c, int(np.argmax(np.abs(c))) / SR


def short_whoosh():
    return s_whoosh(.32, 500, 1400, 700, 1.2, 1.6)


def breath():
    return s_whoosh(.7, 250, 900, 400, .8, 2.6)


def film():
    f = s_filmclick(); return f, 0.0


def paper():
    return s_paper()


def sfx(name, dur, events, gain_db=-1.5):
    """events: [(sound_and_offset, at, level)]"""
    write_wav(name, mix(dur, [(s, at, off, lvl) for (s, off), at, lvl in events], gain_db=gain_db))


SAFE = "Turn on Safe zones to check."

# ------------------------------------------------------------------ 1. Repeated stack, new movement
section("r3-stack", "Repeated stack: new movement",
        "You liked the idea but not the effect. Same rows, same safe-zone size, same monochrome card. Only the movement changes, "
        "and each uses one of your kept motions with the sound you kept for it. The last one is the same on dusty blue (your Maybe).", 1)
PAL["blue_stack"] = {**PAL["blue"]}


def stack_css(rgb):
    return (".t { display:flex; flex-direction:column; align-items:center; font-stretch:condensed; font-weight:800; text-transform:uppercase;"
            " line-height:1.02; letter-spacing:-.005em; white-space:nowrap; } .rw { overflow:hidden; padding:0 4px; } .rw > span { display:inline-block; }"
            + "".join(f" .r{i} {{ font-size:{30 + i * 11}px; color:rgba({rgb},{0.35 + i * 0.1:.2f}); }}" for i in range(7)))


STACK_HTML = "".join(f'<div class="rw"><span class="r{i}">Better than it looks</span></div>' for i in range(7))
RULE_JS = 'anim($(".rule"), [{transform:"scaleX(0)"},{transform:"scaleX(1)"}], {duration:600, delay:350, easing:"' + EASE + '"});'
SMOOTH_ROWS = '$$(".rw").forEach((r, i) => anim(r, [{opacity:0, transform:"translateY(28px)"},{opacity:1, transform:"none"}], {duration:520, delay:350 + i*90, easing:"' + EASE + '"}));'
SNAPPY_ROWS = '$$(".rw > span").forEach((r, i) => anim(r, [{transform:"translateY(105%)"},{transform:"none"}], {duration:240, delay:350 + i*60, easing:"' + SNAP + '"}));'
FILMIC = ('anim($(".t"), [{opacity:0, filter:"blur(24px) brightness(1.6)", transform:"scale(1.04)"},{opacity:1, filter:"blur(0) brightness(1)", transform:"scale(1)"}], {duration:800, delay:350, easing:"cubic-bezier(.25,.6,.2,1)"});'
          'anim($(".stage"), [{transform:"scale(1)"},{transform:"scale(1.015)"}], {duration:2600, easing:"linear"});')
STACKS = [
    ("r3-st1", "mono", "242,238,232", "Rows rise in", "Each row rises 28px and fades in, top to bottom, 90 ms apart (your smooth rise), with the soft breath of air under it.",
     SMOOTH_ROWS, [(breath(), .75, 1)], "Breath of air (kept, synthesised)"),
    ("r3-st2", "mono", "242,238,232", "Rows slide up from masks", "Each row slides up from behind its own mask, 60 ms apart (your snappy mask), with the short whoosh.",
     SNAPPY_ROWS, [(short_whoosh(), .6, 1)], "Short whoosh (kept, synthesised)"),
    ("r3-st3", "mono", "242,238,232", "Whole stack pulls into focus", "The whole stack pulls from blur to sharp at once, then drifts slowly (your filmic focus), with the film click.",
     FILMIC, [(film(), .35, 1)], "Film click (kept, synthesised)"),
    ("r3-st4", "blue_stack", "60,81,130", "Rows rise in, dusty blue", "The first option on your dusty blue scheme: dusty blue rows on pale grey-white. Fixes the Maybe on round 2's dusty blue stack.",
     SMOOTH_ROWS, [(breath(), .75, 1)], "Breath of air (kept, synthesised)"),
]
for i, (cid, pal, rgb, label, desc, js, ev, src) in enumerate(STACKS):
    page(cid, pal, f'<div class="card"></div>{DETAILS}<div class="stage"><div class="t">{STACK_HTML}</div></div>', css=stack_css(rgb), js=js + RULE_JS)
    sfx(cid, 2.6, ev)
    card(cid, "r3-stack", label, desc + " " + SAFE, i + 1, "card", sound=True, source=src)

# ------------------------------------------------------------------ 2. Handwritten card, new movement
section("r3-hand", "Handwritten card: new movement",
        "You loved the idea but not the left-to-right wipe. Same paper card, blue ink and line over your voice. Only the movement changes, "
        "using your kept motions. Each lands with the soft click.", 2)
FREE = """<!doctype html><html><head><meta charset="utf-8"><style>
{caveat}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:1080px; height:1920px; overflow:hidden; background:{bg}; font-family:"Helvetica Neue"; -webkit-font-smoothing:antialiased; }}
.grain {{ position:absolute; inset:0; width:1080px; height:1920px; mix-blend-mode:overlay; opacity:{grain}; pointer-events:none; }}
{css}
</style></head><body>{body}<canvas class="grain" id="grain" width="360" height="640"{gh}></canvas><script>
window.DURATION = {dur}; const A = [];
function anim(el, kf, o) {{ const a = el.animate(kf, {{ fill:"both", ...o }}); a.pause(); A.push(a); return a; }}
const $ = (q) => document.querySelector(q), $$ = (q) => [...document.querySelectorAll(q)];
const G = $("#grain"), gx = G.getContext("2d");
function grain(f) {{ if (G.hidden) return; let s = (f * 9301 + 49297) % 233280; const img = gx.createImageData(360, 640), d = img.data;
  for (let i = 0; i < d.length; i += 4) {{ s = (s * 9301 + 49297) % 233280; const v = (s / 233280) * 255; d[i] = d[i+1] = d[i+2] = v; d[i+3] = 255; }} gx.putImageData(img, 0, 0); }}
{js}
window.seek = (t) => {{ for (const a of A) a.currentTime = t*1000; if (window.onFrame) window.onFrame(t); grain(Math.round(t*30)); }};
window.seek(0);
</script></body></html>"""


def free(cid, body, css="", js="", bg="transparent", grain=0.0, dur=2.9):
    (HERE / "pages" / f"{cid}.html").write_text(FREE.format(caveat=CAVEAT, bg=bg, css=css, body=body, js=js, grain=grain, dur=dur,
                                                             gh="" if grain else " hidden"))


LINES = ["act like the", "business you", "want to become."]
HAND_CSS = (' .note { position:absolute; left:150px; top:620px; font:600 128px/1.08 "Caveat"; color:#2B3E6E; }'
            ' .ln { display:block; } .wd { display:inline-block; }'
            ' .by { position:absolute; left:156px; top:1120px; font:500 26px/1 "Helvetica Neue"; letter-spacing:.2em; text-transform:uppercase; color:rgba(43,62,110,.6); }')
HAND_LINES = '<div class="note">' + "".join(f'<span class="ln">{l}</span>' for l in LINES) + '</div><div class="by">— vale studio</div>'
HAND_WORDS = '<div class="note">' + "".join('<span class="ln">' + " ".join(f'<span class="wd">{w}</span>' for w in l.split()) + "</span>" for l in LINES) + '</div><div class="by">— vale studio</div>'
CUT = lambda sel, ms: f'anim($("{sel}"), [{{opacity:0}},{{opacity:0,offset:.999}},{{opacity:1}}], {{duration:{ms}, easing:"steps(1,end)"}});'
FADE_BY = lambda ms: 'anim($(".by"), [{opacity:0},{opacity:1}], {duration:500, delay:' + str(ms) + ', easing:"' + EASE + '"});'
HANDS = [
    ("r3-h1", "Hard cut", "The whole note appears in one frame, like Tom's cut scenes. Nothing moves.", HAND_LINES,
     CUT(".note", 350) + CUT(".by", 350)),
    ("r3-h2", "Line by line", "Each line rises 28px and fades in, 260 ms apart (your smooth rise).", HAND_LINES,
     '$$(".ln").forEach((l, i) => anim(l, [{opacity:0, transform:"translateY(28px)"},{opacity:1, transform:"none"}], {duration:520, delay:350 + i*260, easing:"' + EASE + '"}));' + FADE_BY(1300)),
    ("r3-h3", "Pulls into focus", "The note pulls from blur to sharp in 800 ms (your filmic focus), then the sign-off fades in.", HAND_LINES,
     'anim($(".note"), [{opacity:0, filter:"blur(24px)", transform:"scale(1.04)"},{opacity:1, filter:"blur(0)", transform:"scale(1)"}], {duration:800, delay:350, easing:"cubic-bezier(.25,.6,.2,1)"});' + FADE_BY(1250)),
    ("r3-h4", "Word by word", "Each word fades in at talking pace, 110 ms apart, like ink landing. No wipe.", HAND_WORDS,
     '$$(".wd").forEach((w, i) => anim(w, [{opacity:0},{opacity:1}], {duration:260, delay:350 + i*110, easing:"' + EASE + '"}));' + FADE_BY(1500)),
]
for i, (cid, label, desc, body, js) in enumerate(HANDS):
    free(cid, body, css=HAND_CSS, js=js, bg="#F3F1EC", grain=.16)
    sfx(cid + "_sfx", 2.9, [(click(), .35, 1)], gain_db=-9)
    card(cid, "r3-hand", label, desc, i + 1, "full", sound=True, source="Your voice plus the soft click (kept, synthesised)")

# ------------------------------------------------------------------ 3. The light scheme
section("r3-light", "Your light scheme",
        "Round 2's Maybe: pale ground, off-black type, a dusty blue key word. Same words and hard cut; each option changes one thing to settle it. "
        "(Blue inside the dark monochrome was dropped, so it stays out.)", 3)
A_CSS = TEXT_CSS.format(w=700, s=150, ls="-.035em", extra="") + " .acc { color: var(--acc); }"
PAL["paper_blueword"] = {**PAL["light_blueword"], "bg": "#F3F1EC"}
LIGHT = [
    ("r3-l1", "paper_blueword", "Warm paper ground", "The cool pale grey becomes the warm paper of your handwritten card (#F3F1EC). Type and blue word unchanged.",
     A_CSS, words_html(WORDS, True), HARD_CUT_JS),
    ("r3-l2", "light_blueword", "Handwritten blue word", "The key word is written in blue ink (Caveat) instead of blue Helvetica, bringing in the handwriting you kept.",
     A_CSS + CAVEAT + ' .acc { font:600 196px/.8 "Caveat"; letter-spacing:0; margin-right:.12em; }', words_html(WORDS, True), HARD_CUT_JS),
    ("r3-l3", "light_blueword", "Blue word, hand underline", "The blue key word gets a hand-drawn blue underline that draws on after the cut.",
     A_CSS + ' .acc { position:relative; } .ul { position:absolute; left:-2%; width:104%; bottom:-28px; height:36px; overflow:visible; }',
     '<span class="w acc">better<svg class="ul" viewBox="0 0 400 36" preserveAspectRatio="none"><path id="ul" d="M4 22 C 90 10, 230 32, 396 12" stroke="#3C5182" stroke-width="9" fill="none" stroke-linecap="round"/></svg></span> '
     + " ".join(f'<span class="w">{w}</span>' for w in WORDS[1:]),
     HARD_CUT_JS + 'const u = $("#ul"), L = u.getTotalLength(); u.style.strokeDasharray = L; anim(u, [{strokeDashoffset:L},{strokeDashoffset:0}], {duration:520, delay:700, easing:"cubic-bezier(.45,.05,.2,1)"});'),
]
for i, (cid, pal, label, desc, css, inner, js) in enumerate(LIGHT):
    page(cid, pal, f'<div class="card"></div>{DETAILS}<div class="stage"><div class="t">{inner}</div></div>', css=css, js=js)
    card(cid, "r3-light", label, desc, i + 1, "card")

# ------------------------------------------------------------------ 4. Big moments
section("r3-big", "Big moments",
        "Both low hits were dropped and the whooshes were kept, so these mark a big moment another way. Same shot, same hard cut to the monochrome card on \"easier\". "
        "Only the sound changes. Open one to hear it.", 4)
BIG_BODY = (f'<div id="all"><div class="card"></div>{DETAILS}<div class="stage"><div class="t"><span class="w acc">easier.</span></div></div></div>')
BIG_CSS = A_CSS + " #all { position:absolute; inset:0; } .t { font-size:190px; }"
BIG_JS = CUT("#all", 1150) + 'anim(G, [{opacity:0},{opacity:0,offset:.999},{opacity:.2}], {duration:1150, easing:"steps(1,end)"});'
BIGS = [
    ("r3-b1", "Short whoosh into the cut", "Your kept short whoosh peaks exactly on the cut, under the voice.", [(short_whoosh(), 1.15, 1)], None),
    ("r3-b2", "Breath of air into the cut", "Your kept breath of air swells into the cut. Softer, more felt than heard.", [(breath(), 1.15, 1)], None),
    ("r3-b3", "Silence", "No sound effect at all: the voice and the room drop out on the cut, and the card holds in silence. The quiet is the hit.", [], 1.15),
    ("r3-b4", "Film click", "Your kept film click (a shutter double click) lands on the cut.", [(film(), 1.15, 1)], None),
]
for i, (cid, label, desc, ev, cut) in enumerate(BIGS):
    page(cid, "mono", BIG_BODY, css=BIG_CSS, js=BIG_JS, dur=2.9, body_bg="transparent")
    if ev:
        sfx(cid + "_sfx", 2.9, ev, gain_db=-8)
    extra = {"voicecut": cut} if cut else {}
    card(cid, "r3-big", label, desc, i + 1, "overlay", sound=True, source="Your voice" + (" plus a kept sound (synthesised)" if ev else ", cut to silence"), **extra)

# ------------------------------------------------------------------ 5. Split screens, pushed
section("r3-split", "Split screen, pushed further",
        "You kept all three splits. Same walk-and-talk underneath, same hard 940px split and monochrome panel unless noted. Each option changes what the panel shows, "
        "with the kept sound that fits its movement. Open one to hear it.", 5)
SPLIT_TPL = """<!doctype html><html><head><meta charset="utf-8"><style>
:root {{ --panel:{panel}; --fg:{fg}; --sub:{sub}; --line:{line}; --acc:{acc}; --stroke:{stroke}; --tile:{tile}; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:1080px; height:1920px; overflow:hidden; background:transparent; font-family:"Helvetica Neue"; color:var(--fg); -webkit-font-smoothing:antialiased; }}
.panel {{ position:absolute; {panelpos} background:var(--panel); {panelextra} overflow:hidden; }}
.lab {{ position:absolute; left:{px}px; top:{ly}px; font:500 22px/1 "Helvetica Neue"; letter-spacing:.24em; text-transform:uppercase; color:var(--sub); }}
.idx {{ position:absolute; right:{px}px; top:{ly}px; font:500 22px/1 "Helvetica Neue"; letter-spacing:.18em; color:var(--sub); }}
.rule {{ position:absolute; left:{px}px; right:{px}px; top:{ry}px; height:1px; background:var(--line); transform-origin:left; }}
.num {{ position:absolute; left:{px}px; font-weight:700; letter-spacing:-.04em; line-height:1; font-variant-numeric:tabular-nums; }}
.cap {{ position:absolute; left:{px}px; font:500 30px/1.2 "Helvetica Neue"; color:var(--sub); }}
svg.ch {{ position:absolute; left:{px}px; overflow:visible; }}
.grid line {{ stroke:var(--line); stroke-width:1; }}
{css}
</style></head><body>
<div class="panel"><div class="lab">{label}</div><div class="idx">01 / 04</div><div class="rule"></div>{inner}</div>
<script>
window.DURATION = 2.9; const A = [];
function anim(el, kf, o) {{ const a = el.animate(kf, {{ fill:"both", ...o }}); a.pause(); A.push(a); return a; }}
const $ = (q) => document.querySelector(q), $$ = (q) => [...document.querySelectorAll(q)];
const ease3 = (k) => 1 - Math.pow(1 - Math.min(1, Math.max(0, k)), 3);
anim($(".rule"), [{{transform:"scaleX(0)"}},{{transform:"scaleX(1)"}}], {{duration:600, delay:150, easing:"{ease}"}});
{js}
window.seek = (t) => {{ for (const a of A) a.currentTime = t*1000; if (window.onFrame) window.onFrame(t); }};
window.seek(0);
</script></body></html>"""
DARK = dict(panel="#151413", fg="#F2EEE8", sub="rgba(242,238,232,.55)", line="rgba(242,238,232,.18)", acc="#E6D8BC", stroke="#F2EEE8", tile="#1E1C1B")
LIGHTP = dict(panel="#E4E4DF", fg="#151413", sub="rgba(21,20,19,.55)", line="rgba(21,20,19,.16)", acc="#3C5182", stroke="#3C5182", tile="#F4F2EE")
HARDG = dict(panelpos="left:0; right:0; top:0; height:940px;", panelextra="", px=110, ly=268, ry=312)
FLOATG = dict(panelpos="left:90px; right:90px; top:220px; height:700px;", panelextra="border-radius:30px; box-shadow:0 40px 80px rgba(0,0,0,.45);", px=60, ly=56, ry=98)
PTS = [(0, 300), (90, 285), (180, 290), (270, 240), (360, 225), (450, 170), (540, 150), (630, 95), (720, 60), (810, 20)]


def line_chart(w, h, top, stroke):
    sx, sy = w / 810, h / 300
    d = "M" + " L".join(f"{x * sx:.1f} {y * sy:.1f}" for x, y in PTS)
    grid = "".join(f'<line x1="0" x2="{w}" y1="{h * k / 3:.1f}" y2="{h * k / 3:.1f}"/>' for k in range(4))
    lx, ly = PTS[-1][0] * sx, PTS[-1][1] * sy
    return (f'<svg class="ch" style="top:{top}px;width:{w}px;height:{h}px" viewBox="0 0 {w} {h}"><g class="grid">{grid}</g>'
            f'<path id="line" d="{d}" fill="none" stroke="{stroke}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle id="dot" cx="{lx:.1f}" cy="{ly:.1f}" r="11" fill="var(--acc)" style="transform-origin:{lx:.1f}px {ly:.1f}px"/></svg>')


LINE_JS = ('const p = $("#line"), L = p.getTotalLength(); p.style.strokeDasharray = L;'
           'anim(p, [{strokeDashoffset:L},{strokeDashoffset:0}], {duration:1300, delay:350, easing:"cubic-bezier(.45,.05,.2,1)"});'
           'anim($("#dot"), [{opacity:0, transform:"scale(.2)"},{opacity:1, transform:"scale(1)"}], {duration:260, delay:1600, easing:"' + EASE + '"});'
           'window.onFrame = (t) => { $("#num").textContent = Math.round(30 * ease3((t - .35) / 1.3)); };')
BARS = [5, 9, 14, 19, 25, 30]
bar_svg = ('<svg class="ch" style="top:610px;width:860px;height:260px" viewBox="0 0 860 260"><g class="grid">'
           + "".join(f'<line x1="0" x2="860" y1="{260 * k / 3:.1f}" y2="{260 * k / 3:.1f}"/>' for k in range(4)) + "</g>"
           + "".join(f'<rect class="bar" x="{i * 152}" y="{260 - v / 30 * 250:.1f}" width="100" height="{v / 30 * 250:.1f}" rx="6" fill="{"var(--acc)" if i == 5 else "var(--stroke)"}" '
                     f'style="transform-origin:{i * 152 + 50}px 260px"/>' for i, v in enumerate(BARS)) + "</svg>")
SPLITS = [
    ("r3-sp1", "Number with a progress line", "Your Maybe, pushed: the big number counts to 30 while a thin progress line fills under it, with a soft click when it lands. Still simple, but it reads as progress.",
     dict(**DARK, **HARDG, label="Posts this month",
          inner='<div class="num" id="num" style="top:370px;font-size:300px">0</div><div class="track" style="position:absolute;left:110px;right:110px;top:720px;height:6px;border-radius:3px;background:var(--line)">'
                '<div id="fill" style="height:100%;border-radius:3px;background:var(--acc);transform-origin:left"></div></div><div class="cap" style="top:760px">from one shoot day</div>',
          css="", js='window.onFrame = (t) => { const e = ease3((t - .35) / 1.3); $("#num").textContent = Math.round(30 * e); $("#fill").style.transform = `scaleX(${e})`; };'),
     "shift", [(click(), 1.65, 1)]),
    ("r3-sp2", "Bar chart grows", "Instead of the line chart, six bars grow one after another as the number counts to 30; the last bar is cream. Soft click as the last bar lands.",
     dict(**DARK, **HARDG, label="Posts this month",
          inner='<div class="num" id="num" style="top:370px;font-size:150px">0</div><div class="cap" style="top:530px">from one shoot day</div>' + bar_svg, css="",
          js='$$(".bar").forEach((b, i) => anim(b, [{transform:"scaleY(0)"},{transform:"scaleY(1)"}], {duration:500, delay:350 + i*120, easing:"' + EASE + '"}));'
             'window.onFrame = (t) => { $("#num").textContent = Math.round(30 * ease3((t - .35) / 1.1)); };'),
     "shift", [(click(), 1.45, 1)]),
    ("r3-sp3", "Stat cards in the panel", "Your kept stat cards (1 / 30 / 0) stack into the panel above the shot, each landing with the paper slide.",
     dict(**DARK, **HARDG, label="One shoot day",
          inner="".join(f'<div class="tile" style="top:{370 + i * 175}px"><b>{b}</b><span>{s}</span></div>' for i, (b, s) in enumerate([("1", "shoot day"), ("30", "posts"), ("0", "stress")])),
          css=".tile { position:absolute; left:110px; right:110px; height:150px; padding:0 44px; border-radius:26px; background:var(--tile); border:1px solid rgba(242,238,232,.08);"
              " box-shadow:0 24px 50px rgba(0,0,0,.35); display:flex; justify-content:space-between; align-items:center; }"
              " .tile b { font:700 84px/1 'Helvetica Neue'; letter-spacing:-.04em; } .tile span { font:500 30px/1 'Helvetica Neue'; color:var(--sub); }",
          js='$$(".tile").forEach((el, i) => anim(el, [{opacity:0, transform:"translateY(90px)"},{opacity:1, transform:"none"}], {duration:520, delay:400 + i*380, easing:"' + EASE + '"}));'),
     "shift", [(paper(), .92 + i * .38, .9) for i in range(3)]),
    ("r3-sp4", "Prompt bar in the panel", "Your kept light prompt bar, typing inside the panel instead of over your face. Lands with the soft click.",
     dict(**DARK, **HARDG, label="Vale Studio",
          inner='<div class="sm" style="position:absolute;left:110px;top:430px">Ask anything</div><div class="bar2" id="c"><div class="txt" id="tx"></div><div class="btn"><svg viewBox="0 0 24 24"><path d="M12 19V5M5 12l7-7 7 7"/></svg></div></div>',
          css=".sm { font:500 30px/1 'Helvetica Neue'; color:var(--sub); }"
              " .bar2 { position:absolute; left:110px; right:110px; top:500px; border-radius:30px; padding:26px 26px 26px 36px; background:#F4F0EC; color:#151413; display:flex; align-items:center; gap:22px; box-shadow:0 24px 60px rgba(0,0,0,.35); }"
              " .txt { flex:1; font:500 40px/1.25 'Helvetica Neue'; letter-spacing:-.01em; white-space:nowrap; overflow:hidden; }"
              " .btn { width:68px; height:68px; border-radius:50%; display:grid; place-items:center; flex:none; background:#151413; color:#F4F0EC; }"
              " .btn svg { width:28px; height:28px; fill:none; stroke:currentColor; stroke-width:3; stroke-linecap:round; stroke-linejoin:round; }",
          js='anim($("#c"), [{opacity:0, transform:"translateY(-36px)"},{opacity:1, transform:"none"}], {duration:480, delay:320, easing:"' + EASE + '"});'
             'const full = "make my business look as good online"; window.onFrame = (t) => { const k = Math.max(0, Math.min(1, (t - .55) / .9));'
             ' $("#tx").textContent = full.slice(0, Math.round(full.length * k)) + (k < 1 && Math.floor(t*4)%2 ? "|" : ""); };'),
     "shift", [(click(), .8, 1)]),
    ("r3-sp5", "Floating card, light", "Your kept floating card in the light scheme: pale card, dusty blue line, over the softened shot. Soft click as the dot lands.",
     dict(**LIGHTP, **FLOATG, label="Posts this month",
          inner='<div class="num" id="num" style="top:150px;font-size:150px">0</div><div class="cap" style="top:310px">from one shoot day</div>' + line_chart(780, 220, 400, LIGHTP["stroke"]),
          css="", js='anim($(".panel"), [{opacity:0, transform:"translateY(40px)"},{opacity:1, transform:"none"}], {duration:520, easing:"' + EASE + '"});' + LINE_JS),
     "blurbg", [(click(), 1.62, 1)]),
]
for i, (cid, label, desc, kw, mode, ev) in enumerate(SPLITS):
    (HERE / "pages" / f"{cid}.html").write_text(SPLIT_TPL.format(ease=EASE, **kw))
    sfx(cid + "_sfx", 2.9, ev, gain_db=-9)
    card(cid, "r3-split", label, desc, i + 1, mode, sound=True, source="Your voice plus a kept sound (synthesised)")

# ------------------------------------------------------------------ 6. Animations, pushed
section("r3-anim", "Animations, pushed further",
        "You kept all four. The first fixes the arrow you flagged; the rest are new explainer moments on the same monochrome card, moving with your kept smooth ease and kept sounds. "
        "Same story: one shoot day becomes a month of posts. Open one to hear it.", 6)
ANIM_CSS = A_CSS + CAVEAT + (
    " .sm { font:500 30px/1.2 'Helvetica Neue'; color:var(--sub); }"
    " .big { font:700 150px/1 'Helvetica Neue'; letter-spacing:-.04em; font-variant-numeric:tabular-nums; }"
    " .col { display:flex; flex-direction:column; gap:28px; align-items:center; }"
    " .note { font:600 80px/1 'Caveat'; color:var(--acc); }")
CAL_CELLS = "".join(f'<div class="cell{" off" if k < 2 or k > 31 else ""}"></div>' for k in range(35))
ANIMS = [
    ("r3-an1", "Handwritten note, arrow fixed", "Round 2's note and arrow, with the arrow redrawn inside the safe zone and pointing back up at the line. " + SAFE,
     '<div class="col"><div class="t">one day<br>of filming.</div>'
     '<svg width="220" height="120" viewBox="0 0 220 120" style="overflow:visible;margin:-6px 0 -10px"><path id="ar" d="M70 112 C 40 80, 60 36, 120 14 M120 14 L92 10 M120 14 L106 40" stroke="#E6D8BC" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'
     '<div class="note" id="nt">= a month of posts</div></div>',
     CUT(".t", 350)
     + 'anim($("#nt"), [{clipPath:"inset(0 100% 0 0)"},{clipPath:"inset(0 0 0 0)"}], {duration:900, delay:900, easing:"cubic-bezier(.4,0,.2,1)"});'
     'const a = $("#ar"), L = a.getTotalLength(); a.style.strokeDasharray = L; anim(a, [{strokeDashoffset:L},{strokeDashoffset:0}], {duration:600, delay:1750, easing:"' + EASE + '"});',
     ".t { font-size:150px; }", [(film(), .9, .8)]),
    ("r3-an2", "Before and after", "Two columns split by a hairline that draws down: 4 posts a month before, 30 after. Each side rises in and counts up, with a soft click as each lands.",
     '<div class="ba"><div class="side" id="s1"><div class="sm">before</div><div class="big" id="n1">0</div><div class="sm">posts a month</div></div>'
     '<div class="div"></div><div class="side" id="s2"><div class="sm">after one shoot day</div><div class="big acc" id="n2">0</div><div class="sm">posts a month</div></div></div>',
     'anim($(".div"), [{transform:"scaleY(0)"},{transform:"scaleY(1)"}], {duration:600, delay:300, easing:"' + EASE + '"});'
     '["#s1", "#s2"].forEach((s, i) => anim($(s), [{opacity:0, transform:"translateY(28px)"},{opacity:1, transform:"none"}], {duration:520, delay:400 + i*600, easing:"' + EASE + '"}));'
     'const e3 = (k) => 1 - Math.pow(1 - Math.min(1, Math.max(0, k)), 3);'
     'window.onFrame = (t) => { $("#n1").textContent = Math.round(4 * e3((t - .4) / .6)); $("#n2").textContent = Math.round(30 * e3((t - 1.0) / 1.0)); };',
     " .ba { display:flex; align-items:stretch; width:860px; } .side { flex:1; display:flex; flex-direction:column; gap:22px; padding:0 40px; }"
     " .side .big { font-size:200px; } .div { width:1px; background:var(--line); transform-origin:top; }",
     [(click(), .92, .9), (click(), 1.52, .9)]),
    ("r3-an3", "A month fills in", "A month calendar on hairlines: thirty days fill in cream one after another while the count climbs to 30 posts. The breath of air under it, a soft click as the last day fills.",
     '<div class="col" style="gap:34px"><div class="hd"><span class="big" id="cn">0</span><span class="sm">posts this month</span></div>'
     '<div class="dows">' + "".join(f"<span>{d}</span>" for d in "MTWTFSS") + f'</div><div class="cal">{CAL_CELLS}</div></div>',
     'const cells = $$(".cell:not(.off)");'
     'window.onFrame = (t) => { let n = 0; cells.forEach((c, i) => { const on = t >= .6 + i * .045; c.classList.toggle("on", on); if (on) n++; }); $("#cn").textContent = n; };'
     'anim($(".cal"), [{opacity:0, transform:"translateY(28px)"},{opacity:1, transform:"none"}], {duration:520, delay:200, easing:"' + EASE + '"});',
     " .hd { width:820px; display:flex; align-items:baseline; gap:26px; } .hd .big { font-size:150px; }"
     " .dows { width:820px; display:grid; grid-template-columns:repeat(7, 100px); gap:20px; } .dows span { font:500 22px/1 'Helvetica Neue'; letter-spacing:.2em; color:var(--sub); text-align:center; }"
     " .cal { display:grid; grid-template-columns:repeat(7, 100px); gap:20px; } .cell { height:100px; border:1px solid var(--line); border-radius:14px; }"
     " .cell.off { border-color:transparent; } .cell.on { background:var(--acc); border-color:var(--acc); }",
     [(breath(), 1.1, .7), (click(), 1.95, 1)]),
    ("r3-an4", "Reach grows, week by week", "Four bars grow one after another with their numbers (1.2k to 12k); the last bar is cream. A soft click as each lands.",
     '<div class="col" style="align-items:flex-start;width:860px;gap:40px"><div class="sm">Reach, first four weeks</div><div class="bars">'
     + "".join(f'<div class="bc"><div class="val">{v}</div><div class="b{" acc-b" if i == 3 else ""}" style="height:{h}px"></div><div class="wk">week {i + 1}</div></div>'
               for i, (v, h) in enumerate([("1.2k", 60), ("3.4k", 170), ("6.8k", 340), ("12k", 600)])) + "</div></div>",
     '$$(".b").forEach((b, i) => anim(b, [{transform:"scaleY(0)"},{transform:"scaleY(1)"}], {duration:520, delay:400 + i*300, easing:"' + EASE + '"}));'
     '$$(".val").forEach((v, i) => anim(v, [{opacity:0, transform:"translateY(12px)"},{opacity:1, transform:"none"}], {duration:300, delay:800 + i*300, easing:"' + EASE + '"}));',
     " .bars { display:flex; align-items:flex-end; gap:66px; height:720px; border-bottom:1px solid var(--line); }"
     " .bc { width:160px; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; gap:16px; height:100%; position:relative; }"
     " .b { width:160px; border-radius:10px 10px 0 0; background:rgba(242,238,232,.28); transform-origin:bottom; } .acc-b { background:var(--acc); }"
     " .val { font:700 44px/1 'Helvetica Neue'; letter-spacing:-.02em; } .wk { position:absolute; bottom:-46px; font:500 24px/1 'Helvetica Neue'; letter-spacing:.14em; color:var(--sub); }",
     [(click(), .92 + i * .3, .9) for i in range(4)]),
]
for i, (cid, label, desc, body, js, css, ev) in enumerate(ANIMS):
    page(cid, "mono", f'<div class="card"></div>{DETAILS}<div class="stage">{body}</div>', css=ANIM_CSS + css, js=js + RULE_JS, dur=3.2)
    sfx(cid, 3.2, ev)
    card(cid, "r3-anim", label, desc, i + 1, "card", sound=True, source="Kept sounds (synthesised)")

# ------------------------------------------------------------------ 7. UI cards, pushed
section("r3-ui", "UI cards, pushed further",
        "You kept the prompt bars and the notification. Same shot, same top band, same light card landing at 0.8 s with the soft click. "
        "Each option adds one thing after it lands. Open one to hear it.", 7)
UI_TPL = """<!doctype html><html><head><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:1080px; height:1920px; overflow:hidden; background:transparent; font-family:"Helvetica Neue"; -webkit-font-smoothing:antialiased; }}
.card {{ position:absolute; left:110px; right:110px; top:245px; border-radius:30px; padding:26px 32px; background:#F4F0EC; color:#151413;
        box-shadow:0 24px 60px rgba(0,0,0,.28), 0 2px 6px rgba(0,0,0,.12); }}
.lab {{ font:500 20px/1 "Helvetica Neue"; letter-spacing:.22em; text-transform:uppercase; opacity:.55; margin-bottom:18px; }}
.row {{ display:flex; align-items:center; gap:22px; }}
.txt {{ flex:1; font:500 40px/1.25 "Helvetica Neue"; letter-spacing:-.01em; white-space:nowrap; overflow:hidden; }}
.btn {{ width:68px; height:68px; border-radius:50%; display:grid; place-items:center; flex:none; background:#151413; color:#F4F0EC; }}
.btn svg {{ width:28px; height:28px; fill:none; stroke:currentColor; stroke-width:3; stroke-linecap:round; stroke-linejoin:round; }}
.av {{ width:72px; height:72px; border-radius:50%; display:grid; place-items:center; font:700 30px/1 "Helvetica Neue"; flex:none; background:#151413; color:#F4F0EC; }}
.meta {{ font:500 24px/1 "Helvetica Neue"; opacity:.55; }}
{css}
</style></head><body>{body}<script>
window.DURATION = 2.9; const A = [];
function anim(el, kf, o) {{ const a = el.animate(kf, {{ fill:"both", ...o }}); a.pause(); A.push(a); return a; }}
const $ = (q) => document.querySelector(q), $$ = (q) => [...document.querySelectorAll(q)];
const e3 = (k) => 1 - Math.pow(1 - Math.min(1, Math.max(0, k)), 3);
{js}
window.seek = (t) => {{ for (const a of A) a.currentTime = t*1000; if (window.onFrame) window.onFrame(t); }};
window.seek(0);
</script></body></html>"""
ARROW = '<svg viewBox="0 0 24 24"><path d="M12 19V5M5 12l7-7 7 7"/></svg>'
CHECK = '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
LAND = 'anim($("#c"), [{opacity:0, transform:"translateY(-36px)"},{opacity:1, transform:"none"}], {duration:480, delay:320, easing:"' + EASE + '"});'
PROMPT = "make my business look as good online"
TYPE = ('const full = "' + PROMPT + '"; const type = (t) => { const k = Math.max(0, Math.min(1, (t - .55) / .9));'
        ' return full.slice(0, Math.round(full.length * k)) + (k < 1 && Math.floor(t*4)%2 ? "|" : ""); };')
BAR = f'<div class="card" id="c"><div class="lab">Vale Studio</div><div class="row"><div class="txt" id="tx"></div><div class="btn" id="b">{ARROW}</div></div></div>'
PRESS = 'anim($("#b"), [{transform:"scale(1)"},{transform:"scale(.86)", offset:.4},{transform:"scale(1)"}], {duration:260, delay:1750, easing:"' + EASE + '"});'
UIS = [
    ("r3-u1", "Prompt bar answers", "After typing, the send button presses and the prompt turns into the answer: \"30 posts, ready to schedule\", with a check. Clicks on the landing and the press.",
     BAR.replace(f'id="b">{ARROW}', f'id="b"><span id="ic1">{ARROW}</span><span id="ic2" style="display:none">{CHECK}</span>'), "",
     LAND + TYPE + PRESS + 'window.onFrame = (t) => { const done = t >= 1.95; $("#tx").textContent = done ? "30 posts, ready to schedule" : type(t);'
     ' $("#ic1").style.display = done ? "none" : "contents"; $("#ic2").style.display = done ? "contents" : "none";'
     ' $("#tx").style.opacity = done ? Math.min(1, (t - 1.95) / .25) : 1; };',
     [(click(), .8, 1), (click(), 1.8, .8)]),
    ("r3-u2", "Cursor clicks send", "After typing, a small pointer glides in and clicks send; the button presses. Clicks on the landing and the press.",
     BAR + '<svg id="cur" viewBox="0 0 24 24" style="position:absolute;width:46px;height:46px;left:0;top:0;filter:drop-shadow(0 4px 8px rgba(0,0,0,.35))">'
           '<path d="M4 2 L4 19 L8.5 15 L11.5 22 L14.5 20.7 L11.6 14 L18 14 Z" fill="#151413" stroke="#F4F0EC" stroke-width="1.6" stroke-linejoin="round"/></svg>', "",
     LAND + TYPE + PRESS + 'window.onFrame = (t) => { $("#tx").textContent = type(t); const k = e3((t - 1.25) / .5);'
     ' const x0 = 640, y0 = 560, x1 = 905, y1 = 340; const c = $("#cur"); c.style.opacity = t < 1.15 ? 0 : Math.min(1, (t - 1.15) / .15);'
     ' const s = t >= 1.75 && t < 1.9 ? .88 : 1; c.style.transform = `translate(${x0 + (x1 - x0) * k}px, ${y0 + (y1 - y0) * k}px) scale(${s})`; };',
     [(click(), .8, 1), (click(), 1.8, .8)]),
    ("r3-u3", "Notifications stack up", "Three enquiries arrive one after another; each new one slides in on top and the older ones tuck behind. A soft click for each.",
     "".join(f'<div class="card nt" id="n{i}"><div class="row"><div class="av">{a}</div><div style="flex:1"><div class="row" style="justify-content:space-between">'
             f'<b style="font:700 34px/1.1 \'Helvetica Neue\'">New enquiry</b><span class="meta">now</span></div>'
             f'<div style="font:500 32px/1.3 \'Helvetica Neue\';margin-top:8px;opacity:.8">{m}</div></div></div></div>'
             for i, (a, m) in enumerate([("S", "Smith Builders: saw your reel, can we chat?"), ("C", "Coast Physio: what would this cost us?"), ("H", "Hart &amp; Co: can you film us next month?")])),
     ".nt { transform-origin:top center; }",
     'const T = [.5, 1.1, 1.7];'
     'window.onFrame = (t) => { T.forEach((ti, i) => { const el = $("#n" + i), k = e3((t - ti) / .48);'
     ' let d = 0; for (let j = i + 1; j < 3; j++) d += e3((t - T[j]) / .48);'
     ' el.style.zIndex = 10 + i; el.style.opacity = k * (1 - d * .3);'
     ' el.style.transform = `translateY(${-36 * (1 - k) + d * 22}px) scale(${1 - d * .05})`; }); };',
     [(click(), ti + .3, 1) for ti in (.5, 1.1, 1.7)]),
    ("r3-u4", "Schedule card ticks off", "A compact \"This week\" card lands, then three posts tick off one by one (Mon reel, Wed carousel, Fri reel). A soft click for each tick.",
     '<div class="card" id="c"><div class="lab">This week</div><div class="row" style="gap:16px">'
     + "".join(f'<div class="chip" id="k{i}"><span class="ck">{CHECK}</span><span><b>{d}</b> {w}</span></div>' for i, (d, w) in enumerate([("Mon", "reel"), ("Wed", "carousel"), ("Fri", "reel")]))
     + "</div></div>",
     " .chip { flex:1; display:flex; align-items:center; gap:14px; padding:16px 18px; border-radius:18px; border:1px solid rgba(21,20,19,.14); font:500 30px/1 'Helvetica Neue'; white-space:nowrap; }"
     " .chip b { font-weight:700; } .ck { width:38px; height:38px; border-radius:50%; border:2px solid rgba(21,20,19,.3); display:grid; place-items:center; flex:none; }"
     " .ck svg { width:22px; height:22px; fill:none; stroke:#F4F0EC; stroke-width:3; stroke-linecap:round; stroke-linejoin:round; opacity:0; }"
     " .chip.on .ck { background:#151413; border-color:#151413; } .chip.on .ck svg { opacity:1; }",
     LAND + 'window.onFrame = (t) => [1.2, 1.55, 1.9].forEach((ti, i) => $("#k" + i).classList.toggle("on", t >= ti));',
     [(click(), .8, 1)] + [(click(), ti, .8) for ti in (1.2, 1.55, 1.9)]),
]
for i, (cid, label, desc, body, css, js, ev) in enumerate(UIS):
    (HERE / "pages" / f"{cid}.html").write_text(UI_TPL.format(body=body, css=css, js=js))
    sfx(cid + "_sfx", 2.9, ev, gain_db=-9)
    card(cid, "r3-ui", label, desc, i + 1, "overlay", sound=True, source="Your voice plus the soft click (kept, synthesised)")

(HERE / "manifest.json").write_text(json.dumps({"sections": sections, "cards": cards}, indent=2))
print(len(cards), "cards in", len(sections), "sections")
