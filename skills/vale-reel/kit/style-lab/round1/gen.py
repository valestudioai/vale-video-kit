"""Round 1 option pages for Style Lab. Writes pages/<card>.html and manifest.json.

Every page is 1080x1920, defines window.DURATION and window.seek(t), and draws everything with CSS/WAAPI so the
renderer can step it frame by frame. One thing changes per option within a section.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
CAVEAT_URI = (HERE.resolve().parents[1] / "brand/fonts/Caveat[wght].ttf").as_uri()
PAGES = HERE / "pages"
PAGES.mkdir(exist_ok=True)

# Colour pairings from the brief (Pinterest boards)
PAL = {
    "mono":  {"bg": "#151413", "fg": "#F2EEE8", "acc": "#E6D8BC", "sub": "rgba(242,238,232,.55)", "line": "rgba(242,238,232,.22)", "grain": .2},
    "cream": {"bg": "#EEE5D3", "fg": "#171513", "acc": "#B9842A", "sub": "rgba(23,21,19,.55)", "line": "rgba(23,21,19,.22)", "grain": .16},
    "kraft": {"bg": "#C6A97F", "fg": "#1A1512", "acc": "#A63A25", "sub": "rgba(26,21,18,.6)", "line": "rgba(26,21,18,.25)", "grain": .18},
    "blue":  {"bg": "#E4E4DF", "fg": "#3C5182", "acc": "#3C5182", "sub": "rgba(60,81,130,.6)", "line": "rgba(60,81,130,.25)", "grain": .14},
}
SUN = """<svg viewBox="-20 -20 40 40" class="sun"><circle r="5.2"/>{rays}</svg>""".format(
    rays="".join(f'<path d="M0 -8.5 Q 2.2 -12 0 -17 Q -2.2 -12 0 -8.5" transform="rotate({a})"/>' for a in range(0, 360, 30)))

BASE = """<!doctype html><html><head><meta charset="utf-8"><style>
:root {{ --bg:{bg}; --fg:{fg}; --acc:{acc}; --sub:{sub}; --line:{line}; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
html,body {{ width:1080px; height:1920px; overflow:hidden; background:{body_bg}; }}
body {{ font-family:"Helvetica Neue", Helvetica, Arial, sans-serif; color:var(--fg); -webkit-font-smoothing:antialiased; }}
.card {{ position:absolute; inset:0; background:var(--bg); }}
.grain {{ position:absolute; inset:0; width:1080px; height:1920px; pointer-events:none; mix-blend-mode:overlay; opacity:{grain}; image-rendering:auto; }}
/* Premium details: corner label, index, hairline, sun mark */
.lab {{ position:absolute; top:268px; left:110px; font:500 22px/1 "Helvetica Neue"; letter-spacing:.24em; text-transform:uppercase; color:var(--sub); }}
.idx {{ position:absolute; top:268px; right:110px; font:500 22px/1 "Helvetica Neue"; letter-spacing:.18em; color:var(--sub); font-variant-numeric:tabular-nums; }}
.rule {{ position:absolute; top:312px; left:110px; right:110px; height:1px; background:var(--line); transform-origin:left; }}
.sun {{ position:absolute; left:508px; top:1520px; width:64px; height:64px; fill:var(--acc); }}
.stage {{ position:absolute; left:110px; right:110px; top:0; bottom:0; display:flex; align-items:center; justify-content:center; text-align:center; }}
.w {{ display:inline-block; }}
{css}
</style></head><body>
{body}
<canvas class="grain" id="grain" width="360" height="640"{grain_hidden}></canvas>
<script>
window.DURATION = {dur};
const G = document.getElementById("grain"), gx = G.getContext("2d");
function grain(f) {{
  if (G.hidden) return;
  let s = (f * 9301 + 49297) % 233280; const img = gx.createImageData(360, 640), d = img.data;
  for (let i = 0; i < d.length; i += 4) {{ s = (s * 9301 + 49297) % 233280; const v = (s / 233280) * 255; d[i] = d[i+1] = d[i+2] = v; d[i+3] = 255; }}
  gx.putImageData(img, 0, 0);
}}
const A = [];
function anim(el, kf, o) {{ const a = el.animate(kf, {{ fill: "both", ...o }}); a.pause(); A.push(a); return a; }}
const $ = (q) => document.querySelector(q), $$ = (q) => [...document.querySelectorAll(q)];
{js}
window.seek = (t) => {{ for (const a of A) a.currentTime = t * 1000; if (window.onFrame) window.onFrame(t); grain(Math.round(t * 30)); }};
window.seek(0);
</script></body></html>"""


def page(card_id, pal, body, css="", js="", dur=2.6, grain=True, body_bg=None):
    p = PAL[pal]
    html = BASE.format(bg=p["bg"], fg=p["fg"], acc=p["acc"], sub=p["sub"], line=p["line"], grain=p["grain"],
                       body_bg=body_bg or p["bg"], css=css, body=body, js=js, dur=dur,
                       grain_hidden="" if grain else " hidden")
    (PAGES / f"{card_id}.html").write_text(html)


DETAILS = '<div class="lab">Vale Studio</div><div class="idx">01 / 04</div><div class="rule"></div>' + SUN
WORDS = ["better", "than", "it", "looks."]
TEXT_CSS = '.t {{ font:{w} {s}px/1.02 "Helvetica Neue"; letter-spacing:{ls}; {extra} }}'


def words_html(words, accent_last=False):
    out = []
    for i, w in enumerate(words):
        cls = "w acc" if accent_last and i == 0 else "w"
        out.append(f'<span class="{cls}">{w}</span>')
    return " ".join(out)


# Shared entrance used where motion is held constant: a hard cut-in at 0.35 s (Tom Noske style)
HARD_CUT_JS = """
anim($(".t"), [{opacity:0},{opacity:0,offset:.999},{opacity:1}], {duration:350, easing:"steps(1,end)"});
anim($(".rule"), [{transform:"scaleX(0)"},{transform:"scaleX(1)"}], {duration:600, delay:350, easing:"cubic-bezier(.2,.8,.2,1)"});
"""

cards, sections = [], []


def section(sid, name, use, order):
    sections.append({"id": sid, "name": name, "use": use, "order": order})


def card(cid, sec, label, desc, order, **kw):
    cards.append({"id": cid, "section": sec, "label": label, "desc": desc, "order": order, **kw})


# ---------------- Section A: colour pairing (same card, same cut, same type) ----------------
section("r1-colour", "Colour: plain-background text cards",
        "Which colour pairing feels like Vale. Same words, same Helvetica, same hard cut, same small details (label, hairline, sun mark, grain). Only the colours change.", 1)
A_CSS = TEXT_CSS.format(w=700, s=150, ls="-.035em", extra="") + " .acc { color: var(--acc); }"
for i, (pal, label, desc) in enumerate([
    ("mono", "Monochrome", "Warm off-black with warm white, the logo cream on the key word, film grain. From your VALE board."),
    ("cream", "Analog cream", "Cream paper with near-black type and the key word in ochre. From your Creative board."),
    ("kraft", "Kraft and brick", "Kraft paper with near-black type and the key word in brick red. Warmer, more retro print."),
    ("blue", "Dusty blue", "Dusty blue type on pale grey-white, one colour only. From \"IT'S ALREADY YOURS\"."),
]):
    cid = f"r1-a{i + 1}"
    page(cid, pal, f'<div class="card"></div>{DETAILS}<div class="stage"><div class="t">{words_html(WORDS, accent_last=True)}</div></div>',
         css=A_CSS, js=HARD_CUT_JS)
    card(cid, "r1-colour", label, desc, i + 1, kind="video")

# ---------------- Section B: how the card text comes in (monochrome held) ----------------
section("r1-motion", "Motion: how the text arrives",
        "Same monochrome card and words. Only the entrance changes, from Tom's hard cut to smooth, snappy, filmic and glitchy accents.", 2)
B_CSS = TEXT_CSS.format(w=700, s=150, ls="-.035em", extra="") + " .acc { color: var(--acc); } .m { display:inline-block; overflow:hidden; vertical-align:top; padding-bottom:.08em; }"
RULE_JS = 'anim($(".rule"), [{transform:"scaleX(0)"},{transform:"scaleX(1)"}], {duration:600, delay:350, easing:"cubic-bezier(.2,.8,.2,1)"});'
B = [
    ("Hard cut", "Appears in one frame, no movement. Tom Noske's cut scene.", HARD_CUT_JS, words_html(WORDS, True)),
    ("Smooth rise", "Each word rises 28px and fades in, 90 ms apart, on a soft ease (520 ms). Calm and clear for teaching.",
     """$$(".w").forEach((w, i) => anim(w, [{opacity:0, transform:"translateY(28px)"},{opacity:1, transform:"none"}], {duration:520, delay:350 + i*90, easing:"cubic-bezier(.2,.8,.2,1)"}));""" + RULE_JS,
     words_html(WORDS, True)),
    ("Snappy mask", "Each word slides up from behind its own mask, 60 ms apart, on a sharp ease (240 ms). Fast and clean.",
     """$$(".m > .w").forEach((w, i) => anim(w, [{transform:"translateY(105%)"},{transform:"none"}], {duration:240, delay:350 + i*60, easing:"cubic-bezier(.7,0,.2,1)"}));""" + RULE_JS,
     " ".join(f'<span class="m"><span class="w{" acc" if i == 0 else ""}">{w}</span></span>' for i, w in enumerate(WORDS))),
    ("Filmic focus", "The line pulls into focus: 24px blur to sharp, 104% to 100% scale, slight exposure lift (800 ms), then a slow drift.",
     """anim($(".t"), [{opacity:0, filter:"blur(24px) brightness(1.6)", transform:"scale(1.04)"},{opacity:1, filter:"blur(0) brightness(1)", transform:"scale(1)"}], {duration:800, delay:350, easing:"cubic-bezier(.25,.6,.2,1)"});
anim($(".stage"), [{transform:"scale(1)"},{transform:"scale(1.015)"}], {duration:2600, easing:"linear"});""" + RULE_JS,
     words_html(WORDS, True)),
    ("Glitch accent", "Cuts in with a 4-frame RGB split and sliced offsets, then sits perfectly still. For key moments only.",
     """anim($(".t"), [{opacity:0},{opacity:0,offset:.999},{opacity:1}], {duration:350, easing:"steps(1,end)"});
window.onFrame = (t) => { const f = Math.round((t - .35) * 30), g = f >= 0 && f < 4, k = [14, -9, 6, -3][f] || 0;
  $(".t").style.textShadow = g ? `${k}px 0 rgba(255,60,60,.75), ${-k}px 0 rgba(60,200,255,.75)` : "none";
  $(".t").style.clipPath = g ? `polygon(0 0,100% 0,100% ${40+f*5}%,${k}% ${40+f*5}%,${k}% ${60-f*4}%,100% ${60-f*4}%,100% 100%,0 100%)` : "none";
  $(".t").style.transform = g ? `translateX(${k*.6}px)` : "none"; };""" + RULE_JS,
     words_html(WORDS, True)),
]
for i, (label, desc, js, inner) in enumerate(B):
    cid = f"r1-b{i + 1}"
    page(cid, "mono", f'<div class="card"></div>{DETAILS}<div class="stage"><div class="t">{inner}</div></div>', css=B_CSS, js=js)
    card(cid, "r1-motion", label, desc, i + 1, kind="video")

# ---------------- Section C: type for big statements (monochrome, hard cut held) ----------------
section("r1-type", "Type: big statements",
        "Same monochrome card and hard cut. Only the typography changes: Helvetica weights, a tall condensed cut, the repeated stack from your Pinterest, and a handwritten note.", 3)
C = [
    ("Helvetica bold, lowercase", "Helvetica Neue Bold 150px, lowercase, tight tracking. Closest to Tom Noske.",
     TEXT_CSS.format(w=700, s=150, ls="-.035em", extra=""), "better than it looks."),
    ("Helvetica medium, sentence case", "Helvetica Neue Medium 120px, sentence case, a calmer more editorial voice.",
     TEXT_CSS.format(w=500, s=120, ls="-.025em", extra=""), "Better than it looks."),
    ("Condensed, uppercase", "Helvetica Neue Condensed Black 210px, uppercase, stacked tall. Poster energy from your BRAND board.",
     TEXT_CSS.format(w=900, s=210, ls="-.01em", extra="font-stretch:condensed; text-transform:uppercase; line-height:.9;"), "Better<br>than it<br>looks"),
    ("Repeated stack", "The line repeats seven times, growing each row in Condensed Bold, the last row running off the edges. From \"IT'S ALREADY YOURS\".",
     ".t { font-stretch:condensed; font-weight:800; text-transform:uppercase; line-height:1; letter-spacing:-.005em; white-space:nowrap; }"
     + "".join(f" .r{i} {{ font-size:{34 + i * 15}px; opacity:{0.35 + i * 0.1:.2f}; }}" for i in range(7)),
     "<br>".join(f'<span class="r{i}">Better than it looks</span>' for i in range(7))),
    ("Bold plus handwritten note", "Helvetica Bold line with a handwritten aside and a hand-drawn underline in logo cream.",
     TEXT_CSS.format(w=700, s=150, ls="-.035em", extra="position:relative;")
     + ' .note { position:absolute; right:-10px; top:-120px; font:600 74px/1 "Caveat"; color:var(--acc); transform:rotate(-6deg); }'
     + ' .ul { position:absolute; left:2%; right:30%; bottom:-34px; height:40px; }',
     'better than<br>it looks.<span class="note">most are</span><svg class="ul" viewBox="0 0 400 40" preserveAspectRatio="none"><path d="M4 26 C 90 12, 210 34, 396 14" stroke="#E6D8BC" stroke-width="7" fill="none" stroke-linecap="round"/></svg>'),
]
for i, (label, desc, css, inner) in enumerate(C):
    cid = f"r1-c{i + 1}"
    font_link = ""
    css_full = css + ' @font-face { font-family:"Caveat"; src:url("' + CAVEAT_URI + '"); }'
    page(cid, "mono", f'<div class="card"></div>{DETAILS}<div class="stage"><div class="t">{inner}</div></div>', css=css_full, js=HARD_CUT_JS)
    card(cid, "r1-type", label, desc, i + 1, kind="video")

(HERE / "manifest.json").write_text(json.dumps({"sections": sections, "cards": cards}, indent=2))
print(f"{len(cards)} card pages in {PAGES}")
