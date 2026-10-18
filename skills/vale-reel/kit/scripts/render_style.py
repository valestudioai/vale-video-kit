"""Apply a Vale editing style (presets/styles/<style>) to a clip's approved cut.

Reads transcript/<clip>/words.json + transcript/<clip>/frames.json and the mastered clip renders/<clip>_master.*.
Writes renders/<clip>/<style>/overlays/*.png, placements.json (timeline frames, per track, plus layout ranges for
split screen and punch-ins) and a preview renders/<clip>/<style>/<clip>_<style>.mp4.

Usage: ~/.cache/video-editor/whisperx-venv/bin/python scripts/render_style.py <style> [clip=BETTER]
"""
import json
import re
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "presets/graphics"))
import vale_graphics as G  # noqa: E402

FF = str(Path.home() / ".local/bin/ffmpeg")
CLIP = sys.argv[2] if len(sys.argv) > 2 else "BETTER"
TDIR = ROOT / "transcript" / CLIP
SRC = next((ROOT / "renders").glob(f"{CLIP}_master.*"))
RAW = next((ROOT / "raw").glob(f"{CLIP}.*"))
FPS = Fraction(json.loads((TDIR / "frames.json").read_text())["fps"])
LUT = ROOT / "presets/look/Vale_Warm_Natural.cube"
FIXES = {"Val": "Vale"}
STOP = {"a", "an", "the", "to", "and", "of", "your", "with", "on", "in", "that", "is", "than", "or", "we", "have",
        "does", "my", "our", "for"}

words = [w for w in json.loads((TDIR / "words.json").read_text())["words"] if w["start"] is not None]
for w in words:
    w["word"] = FIXES.get(w["word"], w["word"])
cut = json.loads((TDIR / "frames.json").read_text())["pieces"]
RAW_END = cut[-1]["sourceOut"] - 0.01
END = cut[-1]["recFrame"] + cut[-1]["frames"]


def tl(t):
    """Raw-clip seconds -> timeline frame (None if cut)."""
    f = Fraction(t) * FPS
    for p in cut:
        if p["inFrame"] <= f < p["outFrame"]:
            return round(f - p["inFrame"] + p["recFrame"])
    return None


def tl_end(t):
    """End frame for something that runs until raw time t. A moment inside a removed pause maps to the end
    of the last kept piece before it, never to the end of the timeline."""
    t = min(t, RAW_END)
    f = tl(t)
    if f is not None:
        return f
    fr = Fraction(t) * FPS
    prev = [p for p in cut if p["outFrame"] <= fr]
    return (prev[-1]["recFrame"] + prev[-1]["frames"]) if prev else 0


def tl_near(t):
    """Like tl, but a moment that was cut maps to the start of the next kept piece."""
    f = tl(t)
    if f is not None:
        return f
    fr = Fraction(t) * FPS
    nxt = [p for p in cut if p["inFrame"] >= fr]
    return nxt[0]["recFrame"] if nxt else END


def find(word, after=0):
    return next(i for i in range(after, len(words)) if words[i]["word"].strip(".,").lower() == word)


def first_shot_change():
    """Raw seconds of the first hard cut (where the B-roll starts)."""
    r = subprocess.run([FF, "-hide_banner", "-i", str(RAW), "-vf", "select='gt(scene,0.3)',showinfo", "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"pts_time:([0-9.]+)", r.stderr)
    return float(m.group(1)) if m else 1e9


def bad_break(left, right):
    lw = left["word"].lower().strip(".,!?")
    proper = left["word"][:1].isupper() and right["word"][:1].isupper() and not re.search(r"[.,!?]$", left["word"])
    return (lw in STOP and not re.search(r"[.,!?]$", left["word"])) or proper


def phrases(max_words):
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        gap = (nxt["start"] - w["end"]) if nxt else 9
        punct = bool(re.search(r"[.,!?]$", w["word"]))
        if nxt is None or (punct and len(cur) >= min(2, max_words)) or gap > 0.35:
            out.append(cur)
            cur = []
        elif len(cur) >= max_words and not (max_words >= 4 and re.search(r"[.!?]$", nxt["word"])):
            k = len(cur)
            while k > 1 and bad_break(cur[k - 1], cur[k] if k < len(cur) else nxt):
                k -= 1
            out.append(cur[:k])
            cur = cur[k:]
    if cur:
        out.append(cur)
    return out


class Plan:
    def __init__(self, style):
        self.style = style
        self.dir = ROOT / "renders" / CLIP / style
        self.ov = self.dir / "overlays"
        if self.ov.exists():
            shutil.rmtree(self.ov)
        self.ov.mkdir(parents=True)
        self.clips, self.split, self.punch = [], [], []
        self.shift = 740  # px the speaker moves down during split screen
        self.n = 0

    def add(self, img, track, s, e, label):
        if s is None or e <= s:
            return
        self.n += 1
        f = self.ov / f"{self.n:03d}_{label}.png"
        img.save(f)
        self.clips.append({"file": f.name, "track": track, "startFrame": s, "endFrame": e, "label": label})

    def captions(self, max_words, render, karaoke, track=1):
        ph = phrases(max_words)
        caps = []
        for pi, p in enumerate(ph):
            text = " ".join(w["word"] for w in p)
            nxt = ph[pi + 1][0]["start"] if pi + 1 < len(ph) else None
            pend = min(p[-1]["end"] + 0.35, nxt) if nxt else p[-1]["end"] + 0.35
            if karaoke:
                for wi, w in enumerate(p):
                    e_t = p[wi + 1]["start"] if wi + 1 < len(p) else pend
                    caps.append((render(text, wi + 1, tl(w["start"])), tl(w["start"]), tl_end(e_t)))
            else:
                caps.append((render(text, None, tl(p[0]["start"])), tl(p[0]["start"]), tl_end(pend)))
        caps = [c for c in caps if c[1] is not None]
        for i in range(len(caps) - 1):  # no overlaps, no flicker gaps
            img, s, e = caps[i]
            ns = caps[i + 1][1]
            if ns < e or 0 < ns - e <= 3:
                caps[i] = (img, s, ns)
        for img, s, e in caps:
            self.add(img, track, s, e, "cap")

    def save(self):
        for c in self.clips:
            c["start"], c["end"], c["frames"] = float(c["startFrame"] / FPS), float(c["endFrame"] / FPS), c["endFrame"] - c["startFrame"]
        data = {"style": self.style, "clip": CLIP, "fps": str(FPS), "timelineFrames": END, "clips": self.clips,
                "splitRanges": self.split, "splitShiftPx": self.shift, "punchRanges": self.punch}
        (self.dir / "placements.json").write_text(json.dumps(data, indent=2))
        return data


def style_justyn(P):
    G.use_palette("vale")
    P.captions(5, lambda t, lit, f: G.caption(t, lit=lit), karaoke=True)
    s = tl(words[find("better")]["start"])
    P.add(G.stack(G.date_line(["16", "10", "October 2026", "Sunshine Coast"]), G.keyword("BETTER")), 2, s,
          tl_end(words[find("online")]["end"] + 0.15), "keyword")
    P.add(G.lower_third("Harry", "Founder, Vale Studio", y=120), 2, tl(words[find("i'm")]["start"]),
          tl_end(words[find("coast")]["end"]), "lower_third")
    i = find("every") - 1
    P.add(G.note_card("Vale Studio", "One full day, every four weeks."), 2, tl(words[i]["start"]),
          tl_end(words[find("business", i)]["end"] + 0.3), "note_card")
    P.add(G.title_stack("You show up", "we handle the rest."), 2, tl(words[find("you", find("content"))]["start"]), END, "title_stack")


def style_cooperson(P):
    broll = tl(first_shot_change()) or END
    P.split.append([0, broll])
    P.add(G.split_panel(), 1, 0, broll, "panel")  # V2 panel, V3 graphics, V4 captions
    # On the panel (just above the seam) while split; on the picture once the B-roll is full frame.
    P.captions(3, lambda t, lit, f: G.mono_caption(t, y=870 if (f or 0) < broll else 960), karaoke=False, track=3)
    beats = [
        (G.ui_title("Better", "than what people see online"), 0, words[find("if")]["start"]),
        (G.checklist([("Builders", "Residential and commercial"), ("Trades", "Crews on the tools"),
                      ("Construction", "South East Queensland")], tag="Who this is for"),
         words[find("if")]["start"], words[find("i'm")]["start"]),
        (G.id_card("Harry", "Founder", "Sunshine Coast"), words[find("i'm")]["start"], None),
    ]
    for img, a, b in beats:
        s = tl(a) if a else 0
        e = min(tl_end(b), broll) if b else broll
        P.add(img, 2, s, e, "panel_graphic")


def style_herk(P):
    P.captions(3, lambda t, lit, f: G.bold_caption(t, y=1470), karaoke=False)
    P.punch.append([tl(words[find("better")]["start"]), tl_end(words[find("online")]["end"] + 0.1)])
    i_this = find("this", find("work"))
    P.punch.append([tl(words[i_this]["start"]), tl_end(words[find("you", i_this)]["end"] + 0.1)])
    P.add(G.list_marker(1, y=150), 2, tl(words[find("if")]["start"]), tl_end(words[find("queensland")]["end"]), "marker")
    P.add(G.list_marker(2, y=150), 2, tl(words[find("every")]["start"]), tl_end(words[find("business", find("every"))]["end"]), "marker")
    P.add(G.list_marker(3, y=150), 2, tl(words[find("you", find("content"))]["start"]), END, "marker")


def style_noske(P):
    broll = tl(first_shot_change()) or END
    # Captions: 1-2 words. On tight framing they sit between chin and shirt logo (y 1035, clear of the logo in both the wide and punched-in framing); over B-roll at 61%.
    P.captions(2, lambda t, lit, f: G.noske_caption(t, y_center=1035 if (f or 0) < broll else 1170), karaoke=False)
    # Second-camera feel: alternate framing every sentence-sized phrase while the speaker is on screen.
    for k, p in enumerate(phrases(5)):
        s, e = tl(p[0]["start"]), tl_end(p[-1]["end"] + 0.2)
        if s is not None and k % 2 == 1 and s < broll:
            P.punch.append([s, min(e, broll), 1.18, 0.30])

    def card(img, a, b, label, min_frames=12):
        s = tl(a)
        e = max(tl_end(b), s + min_frames)
        P.add(img, 2, s, min(e, END), label)

    w = words
    card(G.word_card("better", dark=False), w[find("better")]["start"], w[find("than")]["start"], "card")
    iq = find("queensland")
    card(G.word_card("queensland", dark=True, ghost="south east"), w[iq]["start"], w[iq]["end"] + 0.1, "card")
    iy = find("quality")
    card(G.word_card("quality", dark=False, ghost="does not reflect the"), w[iy]["start"], w[find("work", iy)]["end"], "card")
    ie = find("every")
    card(G.quote_card("every four weeks"), w[ie]["start"], w[find("weeks", ie)]["end"] + 0.1, "card")
    ir = find("rest")
    card(G.word_card("the rest.", dark=True), w[ir - 1]["start"], 23.68, "card")


def style_hybrid(P):
    """Vale hybrid: Noske plain-text cards + Gannon-simple white 50/50 board + Cooperson ink 50/50 cards.
    Built for walk-and-talk selfie footage (white tee, bright sky)."""
    w = words
    INK, WHITE = "#141313", "#FFFFFF"
    P.shift = 700

    def W_(word, after=0):
        return find(word, after)

    def t(i, edge="start"):
        return w[i][edge]

    # --- Split 1 (Gannon white panel): the four types, built row by row as each is named ---------------
    s1a, s1b = tl_near(t(W_("so", W_("types")))), tl_end(t(W_("happening"), "end") + 0.1)
    # --- Split 2 (Cooperson ink panel): goal -> type, building up --------------------------------------
    i_goal = W_("want", W_("clear", W_("goals")))
    s2a, s2b = tl_near(t(i_goal - 2)), tl_end(t(W_("do", W_("industry")), "end") + 0.1)
    P.split += [[s1a, s1b], [s2a, s2b]]

    def in_split(f):
        return f is not None and any(a <= f < b for a, b in P.split)

    def in_white(f):
        return f is not None and s1a <= f < s1b

    # Captions: Noske 1-2 words. Ink with a white glow on the tee/sky; tiny under the white panel; mono on ink.
    def cap(text, lit, f):
        if in_white(f):
            return G.tiny_caption(text, 935, dark=True, size=44)
        if in_split(f):
            return G.mono_caption(text, y=862)
        return G.noske_caption(text, y_center=1060, size=92, color=INK, shadow=WHITE)
    P.captions(2, cap, karaoke=False, track=4)

    # Panels (V2) and their graphics (V3)
    P.add(G.white_panel(), 1, s1a, s1b, "panel_white")
    P.add(G.split_panel(), 1, s2a, s2b, "panel_ink")
    items = [("Education", "Teach your process"), ("Entertainment", "Skits, easy watching"),
             ("Inspirational", "Quotes, voiceovers"), ("Trending", "Formats happening now")]
    marks = [s1a, tl_near(t(W_("education"))), tl_near(t(W_("entertainment"))), tl_near(t(W_("inspirational"))),
             tl_near(t(W_("trending", W_("inspirational")))), s1b]
    for k in range(5):  # state 0 = title only (all faint), then each row goes live as it's named
        img = G.stack(G.types_board("four types of content", items, k - 1 if k else -1), G.asterisk(980, 150, r=28))
        P.add(img, 2, marks[k], marks[k + 1], "board")
    goals = [("Show your process", "That's education", W_("education", i_goal)),
             ("Attract better talent", "That's entertainment", W_("entertainment", i_goal)),
             ("Share some truth", "That's inspirational", W_("inspirational", i_goal)),
             ("Use industry formats", "That's trending", W_("trending", W_("inspirational", i_goal)))]
    starts = [s2a] + [tl_near(t(g[2])) for g in goals[1:]] + [s2b]
    for k in range(4):
        img = G.checklist([(a, b) for a, b, _ in goals[: k + 1]], tag="Match it to your goal", y=200)
        P.add(img, 2, starts[k], starts[k + 1], "goal_cards")

    # --- Noske plain-text cards (V5, full screen) on key words in full-frame sections ------------------
    def card(img, a_idx, b_t, min_frames=14):
        s = tl_near(t(a_idx))
        e = max(tl_end(b_t), s + min_frames)
        if not in_split(s):
            P.add(img, 5, s, min(e, END), "card")
    card(G.word_card("content ideas", dark=False, ghost="how to come up with"), W_("content"), t(W_("ideas"), "end") + 0.1)
    card(G.word_card("big picture", dark=True), W_("big"), t(W_("picture"), "end") + 0.15)
    card(G.word_card("four types.", dark=False, ghost="one of"), W_("four"), t(W_("types", W_("four")), "end") + 0.1)
    ie = W_("easier", W_("match"))
    card(G.word_card("so much easier", dark=True), ie - 2, t(ie, "end") + 0.15)
    card(G.word_card("your goals", dark=False, ghost="clear on"), W_("goals") - 1, t(W_("goals"), "end") + 0.15)
    card(G.quote_card("your next content session."), W_("next"), RAW_END, min_frames=30)

    # --- Second-camera feel: alternate framing per sentence in full-frame sections ---------------------
    for k, p in enumerate(phrases(6)):
        a, b = tl(p[0]["start"]), tl_end(p[-1]["end"] + 0.15)
        if a is not None and k % 2 == 1 and not in_split(a) and not in_split(b - 1):
            P.punch.append([a, b, 1.15, 0.22])


STYLES = {"justyn-editorial": style_justyn, "cooperson-split": style_cooperson, "herk-bold": style_herk,
          "noske-cards": style_noske, "vale-hybrid": style_hybrid}


def render(P, data):
    fc, n = [], len(cut)
    for i, p in enumerate(cut):
        fc.append(f"[0:v]trim=start_frame={p['inFrame']}:end_frame={p['outFrame']},setpts=PTS-STARTPTS[v{i}]")
        fc.append(f"[0:a]atrim=start={float(p['inFrame'] / FPS)}:end={float(p['outFrame'] / FPS)},asetpts=PTS-STARTPTS[a{i}]")
    fc.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
    fc.append(f"[vc]lut3d=file='{LUT}'[base]")
    last = "base"
    sh = data["splitShiftPx"]
    for k, (s, e) in enumerate(data["splitRanges"]):
        fc.append(f"[{last}]split[sa{k}][sb{k}];[sb{k}]crop=1080:{1920 - sh}:0:0,pad=1080:1920:0:{sh}:black[sh{k}];"
                  f"[sa{k}][sh{k}]overlay=0:0:enable='between(n,{s},{e - 1})'[sp{k}]")
        last = f"sp{k}"
    for k, pr in enumerate(data["punchRanges"]):
        s, e = pr[0], pr[1]
        z = pr[2] if len(pr) > 2 else 1.15
        yf = pr[3] if len(pr) > 3 else 0.5
        fc.append(f"[{last}]split[pa{k}][pb{k}];[pb{k}]crop=iw/{z}:ih/{z}:(iw-ow)/2:(ih-oh)*{yf},scale=1080:1920[pz{k}];"
                  f"[pa{k}][pz{k}]overlay=0:0:enable='between(n,{s},{e - 1})'[pu{k}]")
        last = f"pu{k}"
    inputs = ["-i", str(SRC)]
    for k, c in enumerate(sorted(data["clips"], key=lambda c: (c["track"], c["startFrame"])), start=1):
        inputs += ["-i", str(P.ov / c["file"])]
        fc.append(f"[{last}][{k}:v]overlay=0:0:enable='between(n,{c['startFrame']},{c['endFrame'] - 1})'[o{k}]")
        last = f"o{k}"
    out = P.dir / f"{CLIP}_{P.style}.mp4"
    subprocess.run([FF, "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", f"[{last}]", "-map", "[ac]",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-fps_mode", "passthrough",
                    "-c:a", "aac", "-b:a", "256k", str(out)], check=True)
    return out


if __name__ == "__main__":
    style = sys.argv[1]
    P = Plan(style)
    STYLES[style](P)
    data = P.save()
    out = render(P, data)
    print(f"{style}: {len(data['clips'])} overlay clips, split {data['splitRanges']}, punch {data['punchRanges']} -> {out}")
