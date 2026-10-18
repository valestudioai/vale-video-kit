"""Round 1 caption options: transparent caption pages timed to BETTER's first line, composited over graded footage.
Writes cap_pages/<id>.html and appends the caption section and cards to manifest.json.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "cap_pages"
OUT.mkdir(exist_ok=True)
WORDS = [["Your", 0.131, 0.351], ["business", 0.432, 0.772], ["is", 0.832, 0.892], ["better", 1.073, 1.313],
         ["than", 1.353, 1.453], ["what", 1.493, 1.613], ["people", 1.673, 1.894], ["can", 1.914, 2.034],
         ["see", 2.054, 2.234], ["online.", 2.294, 2.595]]

TPL = """<!doctype html><html><head><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:1080px; height:1920px; overflow:hidden; background:transparent; }}
.cap {{ position:absolute; left:110px; right:110px; top:{y}px; transform:translateY(-50%); text-align:center;
        font-family:"Helvetica Neue"; color:#fff; -webkit-font-smoothing:antialiased; {style} }}
.dim {{ opacity:.42; }} .key {{ color:#E6D8BC; }}
</style></head><body><div class="cap" id="cap"></div><script>
window.DURATION = 2.9;
const W = {words}, GROUPS = {groups}, MODE = "{mode}", CASE = "{case}";
const cap = document.getElementById("cap");
const fmt = (s) => CASE === "lower" ? s.toLowerCase() : s;
window.seek = (t) => {{
  // a group shows from its first word's start until the next group starts (last one holds 0.3 s)
  let g = -1;
  for (let i = 0; i < GROUPS.length; i++) {{ const s = W[GROUPS[i][0]][1]; if (t >= s) g = i; }}
  const last = GROUPS[GROUPS.length - 1], end = W[last[last.length - 1]][2] + 0.3;
  if (g < 0 || t > end) {{ cap.innerHTML = ""; return; }}
  cap.innerHTML = GROUPS[g].map((wi) => {{
    const w = W[wi], cls = MODE === "karaoke" && t < w[1] ? "dim" : (MODE === "key" && w[0] === "better" ? "key" : "");
    return `<span class="${{cls}}">${{fmt(w[0])}}</span>`;
  }}).join(" ");
}};
window.seek(0);
</script></body></html>"""

PAIRS = [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
THREES = [[0, 1, 2], [3, 4, 5], [6, 7, 8, 9]]
SHADOW = "text-shadow:0 2px 14px rgba(0,0,0,.45), 0 0 2px rgba(0,0,0,.25);"
OPTS = [
    ("r1-d1", "Tom: 1 to 2 bold words", "Helvetica Neue Bold 96px, lowercase, white, two words at a time, soft shadow. Closest to Tom Noske.",
     f"font-weight:700; font-size:96px; letter-spacing:-.025em; {SHADOW}", PAIRS, "plain", "lower"),
    ("r1-d2", "Gannon: tiny", "Same as Tom's, but small: 46px. Quieter, lets the picture breathe.",
     f"font-weight:700; font-size:46px; letter-spacing:-.01em; {SHADOW}", PAIRS, "plain", "lower"),
    ("r1-d3", "Phrase with spoken words lit", "Three to four words at a time, 80px bold; words not said yet sit at 40% white.",
     f"font-weight:700; font-size:80px; letter-spacing:-.025em; line-height:1.05; {SHADOW}", THREES, "karaoke", "lower"),
    ("r1-d4", "Tom plus one cream word", "Tom's caption, with the key word (\\u201cbetter\\u201d) in your logo cream.",
     f"font-weight:700; font-size:96px; letter-spacing:-.025em; {SHADOW}", PAIRS, "key", "lower"),
    ("r1-d5", "Sentence case, medium", "Helvetica Neue Medium 72px in sentence case, three to four words. More editorial, less punchy.",
     f"font-weight:500; font-size:72px; letter-spacing:-.015em; line-height:1.08; {SHADOW}", THREES, "plain", "as-is"),
]
manifest = json.loads((HERE / "manifest.json").read_text())
manifest["sections"] = [s for s in manifest["sections"] if s["id"] != "r1-captions"]
manifest["cards"] = [c for c in manifest["cards"] if c["section"] != "r1-captions"]
manifest["sections"].append({"id": "r1-captions", "name": "Captions",
                             "use": "Same footage, same words, same position (just under the chin, clear of the shirt logo). Only the caption style changes. Open one to hear it with sound.",
                             "order": 4})
for i, (cid, label, desc, style, groups, mode, case) in enumerate(OPTS):
    (OUT / f"{cid}.html").write_text(TPL.format(y=980, style=style, words=json.dumps(WORDS), groups=json.dumps(groups),
                                                mode=mode, case=case))
    manifest["cards"].append({"id": cid, "section": "r1-captions", "label": label, "desc": desc.replace("\\u201c", "“").replace("\\u201d", "”"),
                              "order": i + 1, "kind": "video", "sound": True})
(HERE / "manifest.json").write_text(json.dumps(manifest, indent=2))
print("caption pages:", len(OPTS))
