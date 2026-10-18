"""Round 2: a Pinterest-led style section (VALE, BRAND and Creative boards). Same walk-and-talk clip and the same
line ("one day of filming") across the section. Overlay pages are transparent and composited over the clip by
build_pin.sh; full-screen pages are rendered as they are. Appends the section to manifest.json.
"""
import json
from pathlib import Path

import numpy as np

import gen2  # noqa: F401  (fresh round 2 manifest)
from gen2 import N, SR, mix, s_click, s_filmclick, s_paper, write_wav

HERE = Path(__file__).parent
CAVEAT_URI = (HERE.resolve().parents[1] / "brand/fonts/Caveat[wght].ttf").as_uri()
(HERE / "pin_pages").mkdir(exist_ok=True)
CAVEAT = '@font-face { font-family:"Caveat"; src:url("' + CAVEAT_URI + '"); }'
SUN = "".join(f'<path d="M0 -8.5 Q 2.2 -12 0 -17 Q -2.2 -12 0 -8.5" transform="rotate({a})"/>' for a in range(0, 360, 30))

TPL = """<!doctype html><html><head><meta charset="utf-8"><style>
{caveat}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:1080px; height:1920px; overflow:hidden; background:{bg}; font-family:"Helvetica Neue"; -webkit-font-smoothing:antialiased; }}
.grain {{ position:absolute; inset:0; width:1080px; height:1920px; mix-blend-mode:overlay; opacity:{grain}; pointer-events:none; }}
{css}
</style></head><body>{body}<canvas class="grain" id="grain" width="360" height="640"{gh}></canvas><script>
window.DURATION = 2.9; const A = [];
function anim(el, kf, o) {{ const a = el.animate(kf, {{ fill:"both", ...o }}); a.pause(); A.push(a); return a; }}
const $ = (q) => document.querySelector(q), $$ = (q) => [...document.querySelectorAll(q)];
const G = $("#grain"), gx = G.getContext("2d");
function grain(f) {{ if (G.hidden) return; let s = (f * 9301 + 49297) % 233280; const img = gx.createImageData(360, 640), d = img.data;
  for (let i = 0; i < d.length; i += 4) {{ s = (s * 9301 + 49297) % 233280; const v = (s / 233280) * 255; d[i] = d[i+1] = d[i+2] = v; d[i+3] = 255; }} gx.putImageData(img, 0, 0); }}
{js}
window.seek = (t) => {{ for (const a of A) a.currentTime = t*1000; if (window.onFrame) window.onFrame(t); grain(Math.round(t*30)); }};
window.seek(0);
</script></body></html>"""


def page(cid, body, css="", js="", bg="transparent", grain=0.0):
    (HERE / "pin_pages" / f"{cid}.html").write_text(TPL.format(caveat=CAVEAT, bg=bg, css=css, body=body, js=js, grain=grain,
                                                               gh="" if grain else " hidden"))


EASE = "cubic-bezier(.2,.8,.2,1)"
CAP = ('.cap { position:absolute; left:110px; right:110px; top:1040px; text-align:center; font:700 92px/1 "Helvetica Neue"; letter-spacing:-.025em;'
       ' color:#141313; text-shadow:0 0 18px rgba(255,255,255,.75), 0 0 4px rgba(255,255,255,.5); }')
CAP_JS = 'window.onFrame = (t) => { const w = [[0,"it becomes"],[.62,"so much"],[1.15,"easier to"],[1.85,"come up with"],[2.4,"content"]]; let s = ""; for (const [a, x] of w) if (t >= a) s = x; $(".cap").textContent = s; };'
OPTS = []

# 1. B&W cinematic with tape timecode (ffmpeg makes the shot black and white with grain; the page adds the overlay)
page("r2-p1", '<div class="tc"><span>TCR</span> <b id="tc">00:01:04.16</b> <span>PLAY</span> <span class="lk">LOCK</span></div><div class="cap"></div>',
     css=CAP + ' .tc { position:absolute; left:110px; top:262px; padding:10px 16px; background:rgba(0,0,0,.82); font:500 30px/1 "Courier New", monospace;'
     ' color:#EDEDED; letter-spacing:.06em; } .tc b { font-weight:500; } .lk { margin-left:18px; }',
     js=CAP_JS.replace("window.onFrame = (t) => {", 'window.onFrame = (t) => { const f = Math.round(t*30), sec = 4 + Math.floor((16 + f) / 30), fr = (16 + f) % 30; $("#tc").textContent = `00:01:${String(sec).padStart(2,"0")}.${String(fr).padStart(2,"0")}`;'))
OPTS.append(("r2-p1", "B&W cinematic", "The shot in black and white with heavy grain and a tape timecode counting, like your \"TCR 00:48:18.25 PLAY LOCK\" pin. Caption is Tom-style in ink with a soft glow so it reads on the white tee.", "bw"))

# 2. Printed photo: cream print border, handwritten caption and date in the bottom margin
page("r2-p2", '<div class="f t"></div><div class="f b"></div><div class="f l"></div><div class="f r"></div>'
     '<div class="hand" id="h">one day of filming.</div><div class="date">17 · 10 · 26</div>',
     css=' .f { position:absolute; background:#EFE9DD; } .f.t { left:0; right:0; top:0; height:200px; } .f.b { left:0; right:0; bottom:0; height:520px; }'
     ' .f.l { left:0; top:0; bottom:0; width:70px; } .f.r { right:0; top:0; bottom:0; width:70px; }'
     ' .hand { position:absolute; left:110px; top:1460px; font:600 104px/1 "Caveat"; color:#2B3E6E; transform:rotate(-2deg); }'
     ' .date { position:absolute; right:110px; top:1610px; font:500 26px/1 "Helvetica Neue"; letter-spacing:.2em; color:rgba(21,20,19,.5); }',
     js='anim($("#h"), [{clipPath:"inset(0 100% 0 0)"},{clipPath:"inset(0 0 0 0)"}], {duration:1100, delay:500, easing:"cubic-bezier(.4,0,.2,1)"});', grain=.08)
OPTS.append(("r2-p2", "Printed photo", "The shot as a print: cream border, blue-ink handwriting writing itself on in the margin, a small date. Analog, from your BRAND board.", "frame"))

# 3. Handwritten card: full screen, blue ink on off-white paper
page("r2-p3", '<div class="note" id="n">act like the<br>business you<br>want to become.</div><div class="by">— vale studio</div>',
     css=' .note { position:absolute; left:150px; top:620px; font:600 128px/1.08 "Caveat"; color:#2B3E6E; }'
     ' .by { position:absolute; left:156px; top:1120px; font:500 26px/1 "Helvetica Neue"; letter-spacing:.2em; text-transform:uppercase; color:rgba(43,62,110,.6); }',
     js='anim($("#n"), [{clipPath:"inset(0 100% 0 0)"},{clipPath:"inset(0 0 0 0)"}], {duration:1500, delay:300, easing:"cubic-bezier(.45,0,.3,1)"});'
        'anim($(".by"), [{opacity:0},{opacity:1}], {duration:500, delay:1800, easing:"' + EASE + '"});',
     bg="#F3F1EC", grain=.16)
OPTS.append(("r2-p3", "Handwritten card", "A full-screen paper card where blue ink writes the line on, like \"Act like the person you want to become\". No footage.", "full"))

# 4. Dusty blue repeated stack, inside the safe zone
page("r2-p4", '<div class="st">' + "".join(f'<div class="r" style="font-size:{30 + i * 11}px;opacity:{.4 + i * .1:.2f}">One day of filming</div>' for i in range(7)) + "</div>",
     css=' .st { position:absolute; left:0; right:0; top:560px; text-align:center; } .r { font-stretch:condensed; font-weight:800; text-transform:uppercase;'
     ' color:#3C5182; line-height:1.04; white-space:nowrap; }',
     js='$$(".r").forEach((r, i) => anim(r, [{opacity:0},{opacity:0, offset:.999},{opacity:+r.style.opacity}], {duration:300 + i*90, easing:"steps(1,end)"}));',
     bg="#E4E4DF", grain=.14)
OPTS.append(("r2-p4", "Dusty blue stack", "\"IT'S ALREADY YOURS\" made Vale's: the line repeating and growing in dusty blue on pale grey, rows cutting in one by one, all inside the safe zone.", "full"))

# 5. Retro sticker slapped on the shot
page("r2-p5", '<div class="stk" id="s"><svg viewBox="-20 -20 40 40" class="sun"><circle r="5.2"/>' + SUN + '</svg><div><b>one day<br>of filming.</b><i>Vale Studio · Sunshine Coast</i></div></div>',
     css=' .stk { position:absolute; left:150px; top:300px; width:780px; padding:34px 40px; display:flex; gap:30px; align-items:center; background:#EFE6D2;'
     ' border-radius:18px; box-shadow:0 18px 40px rgba(0,0,0,.3); border:4px solid #EFE6D2; outline:3px solid #1F1B17; outline-offset:-14px; }'
     ' .sun { width:110px; height:110px; fill:#B9842A; flex:none; } .stk b { display:block; font:700 78px/.95 "Helvetica Neue"; letter-spacing:-.03em; color:#1F1B17; }'
     ' .stk i { display:block; margin-top:14px; font:500 20px/1 "Helvetica Neue"; font-style:normal; letter-spacing:.22em; text-transform:uppercase; color:rgba(31,27,23,.6); }',
     js='anim($("#s"), [{opacity:0, transform:"translateY(-60px) rotate(-12deg) scale(1.06)"},{opacity:1, transform:"translateY(0) rotate(-4deg) scale(1)"}], {duration:420, delay:380, easing:"' + EASE + '"});')
OPTS.append(("r2-p5", "Retro sticker", "A cream print sticker with the sun mark, slapped onto the shot at a slight angle. From your Creative board's stickers and matchbooks.", "overlay"))

# Sounds under the voice
c, f = s_click(), s_filmclick()
p, poff = s_paper()
write_wav("r2-p1_sfx", mix(2.9, [(f, .02, 0, 1)], gain_db=-12))
write_wav("r2-p2_sfx", mix(2.9, [(f, .1, 0, 1)], gain_db=-10))
write_wav("r2-p3_sfx", mix(2.9, [(p, .32 + poff, poff, 1)], gain_db=-6))
write_wav("r2-p4_sfx", mix(2.9, [(c, .3 + i * .09 + i * .0, int(np.argmax(np.abs(c))) / SR, .7) for i in range(7)], gain_db=-6))
write_wav("r2-p5_sfx", mix(2.9, [(p, .8, poff, 1)], gain_db=-9))

manifest = json.loads((HERE / "manifest.json").read_text())
manifest["sections"] = [s for s in manifest["sections"] if s["id"] != "r2-pin"]
manifest["cards"] = [x for x in manifest["cards"] if x["section"] != "r2-pin"]
manifest["sections"].append({"id": "r2-pin", "name": "A style from your Pinterest",
                             "use": "Five treatments taken straight from your VALE, BRAND and Creative boards, on the same walk-and-talk shot and the same line. Open one to hear it.",
                             "order": 6})
for i, (cid, label, desc, mode) in enumerate(OPTS):
    manifest["cards"].append({"id": cid, "section": "r2-pin", "label": label, "desc": desc, "order": i + 1, "kind": "video", "sound": True,
                              "mode": mode, "source": "Your voice plus a kept sound (synthesised)"})
(HERE / "manifest.json").write_text(json.dumps(manifest, indent=2))
print("pinterest options:", len(OPTS))
