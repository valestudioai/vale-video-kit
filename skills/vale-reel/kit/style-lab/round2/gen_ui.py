"""Round 2, UI cards over footage (from justyn.ai: the UI cards and prompt bars, and the polish).
Transparent pages composited over the graded BETTER clip; each card lands at 0.8 s with the kept soft click.
Appends the section to manifest.json and writes audio/<id>_sfx.wav (the click alone; the voice comes from the clip).
"""
import json
from pathlib import Path

import numpy as np

import gen2  # noqa: F401  (re-runs round 2's generator so the manifest is fresh, then we append)
from gen2 import N, SR, mix, s_click, write_wav

HERE = Path(__file__).parent
(HERE / "ui_pages").mkdir(exist_ok=True)

TPL = """<!doctype html><html><head><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:1080px; height:1920px; overflow:hidden; background:transparent; font-family:"Helvetica Neue"; -webkit-font-smoothing:antialiased; }}
.card {{ position:absolute; left:110px; right:110px; top:245px; border-radius:30px; padding:26px 32px; {look}
        box-shadow:0 24px 60px rgba(0,0,0,.28), 0 2px 6px rgba(0,0,0,.12); }}
.lab {{ font:500 20px/1 "Helvetica Neue"; letter-spacing:.22em; text-transform:uppercase; opacity:.55; margin-bottom:18px; }}
.row {{ display:flex; align-items:center; gap:22px; }}
.txt {{ flex:1; font:500 40px/1.25 "Helvetica Neue"; letter-spacing:-.01em; white-space:nowrap; overflow:hidden; }}
.btn {{ width:68px; height:68px; border-radius:50%; display:grid; place-items:center; flex:none; {btn} }}
.btn svg {{ width:28px; height:28px; fill:none; stroke:currentColor; stroke-width:3; stroke-linecap:round; stroke-linejoin:round; }}
.av {{ width:72px; height:72px; border-radius:50%; display:grid; place-items:center; font:700 30px/1 "Helvetica Neue"; flex:none; {av} }}
.meta {{ font:500 24px/1 "Helvetica Neue"; opacity:.55; }}
.pill {{ position:absolute; left:50%; top:258px; transform:translateX(-50%); padding:18px 30px; border-radius:999px; background:#F4F0EC; color:#151413;
        font:500 40px/1 "Helvetica Neue"; letter-spacing:-.01em; white-space:nowrap; box-shadow:0 16px 40px rgba(0,0,0,.25); }}
.pill b {{ font-weight:700; }}
</style></head><body>{body}<script>
window.DURATION = 2.9; const A = [];
function anim(el, kf, o) {{ const a = el.animate(kf, {{ fill:"both", ...o }}); a.pause(); A.push(a); return a; }}
const $ = (q) => document.querySelector(q);
{js}
window.seek = (t) => {{ for (const a of A) a.currentTime = t*1000; if (window.onFrame) window.onFrame(t); }};
window.seek(0);
</script></body></html>"""

ARROW = '<svg viewBox="0 0 24 24"><path d="M12 19V5M5 12l7-7 7 7"/></svg>'
LAND = 'anim($("{sel}"), [{{opacity:0, transform:"translateY(-36px) {extra}"}},{{opacity:1, transform:"translateY(0) {extra}"}}], {{duration:480, delay:320, easing:"cubic-bezier(.2,.8,.2,1)"}});'
TYPE = ('const full = "{text}"; window.onFrame = (t) => {{ const k = Math.max(0, Math.min(1, (t - .55) / .9));'
        ' $("#tx").textContent = full.slice(0, Math.round(full.length * k)) + (k < 1 && Math.floor(t*4)%2 ? "|" : ""); }};')
PROMPT = "make my business look as good online"
OPTS = [
    ("r2-u1", "Prompt bar, light", "A cream prompt bar drops in and types the line, with a round dark send button. justyn.ai's prompt bar in Vale colours.",
     "background:#F4F0EC; color:#151413;", "background:#151413; color:#F4F0EC;", "",
     f'<div class="card" id="c"><div class="lab">Vale Studio</div><div class="row"><div class="txt" id="tx"></div><div class="btn">{ARROW}</div></div></div>',
     LAND.format(sel="#c", extra="") + TYPE.format(text=PROMPT)),
    ("r2-u2", "Prompt bar, dark", "The same prompt bar in the monochrome dark card with a cream send button.",
     "background:rgba(21,20,19,.92); color:#F2EEE8; border:1px solid rgba(242,238,232,.1);", "background:#E6D8BC; color:#151413;", "",
     f'<div class="card" id="c"><div class="lab">Vale Studio</div><div class="row"><div class="txt" id="tx"></div><div class="btn">{ARROW}</div></div></div>',
     LAND.format(sel="#c", extra="") + TYPE.format(text=PROMPT)),
    ("r2-u3", "Notification card", "A phone-style notification slides down: \"New enquiry\" from a builder, with an initial avatar. Shows the result, not the tool.",
     "background:rgba(244,240,236,.96); color:#151413;", "", "background:#151413; color:#F4F0EC;",
     '<div class="card" id="c"><div class="row"><div class="av">S</div><div style="flex:1"><div class="row" style="justify-content:space-between">'
     '<b style="font:700 34px/1.1 \'Helvetica Neue\'">New enquiry</b><span class="meta">now</span></div>'
     '<div style="font:500 32px/1.3 \'Helvetica Neue\';margin-top:8px;opacity:.8">Smith Builders: saw your reel, can we chat?</div></div></div></div>',
     LAND.format(sel="#c", extra="")),
    ("r2-u4", "Pill label", "A small white pill drops in with one bold number. The lightest touch: \"<b>1 day</b> of filming\".",
     "", "", "",
     '<div class="pill" id="c"><b>1 day</b> of filming</div>',
     LAND.format(sel="#c", extra="translateX(-50%)").replace('translateY(-36px) translateX(-50%)', 'translateX(-50%) translateY(-36px)').replace('translateY(0) translateX(-50%)', 'translateX(-50%) translateY(0)')),
]
manifest = json.loads((HERE / "manifest.json").read_text())
manifest["sections"].append({"id": "r2-ui", "name": "UI cards over footage",
                             "use": "From justyn.ai: interface cards that sit on the shot, with polish and warmth. Same clip, same spot in the top band, same landing at 0.8 s with your kept soft click. Each option changes the card. Open one to hear it.",
                             "order": 5})
for i, (cid, label, desc, look, btn, av, body, js) in enumerate(OPTS):
    (HERE / "ui_pages" / f"{cid}.html").write_text(TPL.format(look=look or "display:none;", btn=btn, av=av, body=body, js=js))
    c = s_click()
    write_wav(f"{cid}_sfx", mix(2.9, [(c, .8, int(np.argmax(np.abs(c))) / SR, 1)], gain_db=-9))
    manifest["cards"].append({"id": cid, "section": "r2-ui", "label": label, "desc": desc.replace("<b>", "").replace("</b>", ""), "order": i + 1,
                              "kind": "video", "sound": True, "source": "Soft click (kept, synthesised) under your voice"})
(HERE / "manifest.json").write_text(json.dumps(manifest, indent=2))
print("ui cards:", len(OPTS))
