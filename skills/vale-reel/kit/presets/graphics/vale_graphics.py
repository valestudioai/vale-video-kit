"""Vale Studio on-screen graphics as transparent PNG overlays (1080x1920 vertical).

Styled after reference reel 3 (references/NOTES.md): serif sentence-case captions on a deep plate with
the spoken words lit and the upcoming words dim, bold-caps-over-italic title stacks, huge serif keywords,
a spaced mono date line, a pill label and a note card. Two palettes:
  "vale"   Umber plate, cream text, light stone italic accent   (default, on-brand)
  "forest" the reference's deep green plate, cream text, muted gold accent

  caption(words, lit=None)       words: phrase string; lit: how many words are already spoken (karaoke)
  keyword(word)                  one huge Newsreader word
  date_line(parts)               DM Mono spaced label
  title_stack(line1, line2)      HANKEN EXTRABOLD CAPS / Newsreader italic. on plates
  pill(text, highlight)          white pill, bold sans, highlight span in the plate colour
  note_card(label, text)         cream card: mono label, sans line, round button with arrow
  lower_third(name, role)        name and role on a plate with an accent rule

Demo: ~/.cache/video-editor/whisperx-venv/bin/python presets/graphics/vale_graphics.py --demo
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FONTS = ROOT / "brand/fonts"
W, H = 1080, 1920
SAFE_X = 90

PALETTES = {
    "vale":   {"plate": "#5A504A", "text": "#F4F0EC", "dim": "#C2B5A6", "accent": "#E6D5BC", "ink": "#141313", "card": "#F4F0EC"},
    "forest": {"plate": "#183429", "text": "#F3EDE1", "dim": "#BFB2A1", "accent": "#C4AC5C", "ink": "#141313", "card": "#F3EDE1"},
}
P = dict(PALETTES["vale"])


def use_palette(name):
    P.clear()
    P.update(PALETTES[name])


def rgba(hex_, a=1.0):
    h = hex_.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (round(255 * a),)


def font(kind, size):
    """sans<weight> (e.g. sans600, sans800), serif<weight>, serif-italic, mono500."""
    if kind.startswith("sans"):
        f = ImageFont.truetype(str(FONTS / "HankenGrotesk[wght].ttf"), size)
        f.set_variation_by_axes([int(kind[4:])])
    elif kind == "serif-italic":
        f = ImageFont.truetype(str(FONTS / "Newsreader-Italic[opsz,wght].ttf"), size)
        f.set_variation_by_axes([min(72, max(6, size)), 400])
    elif kind.startswith("serif"):
        f = ImageFont.truetype(str(FONTS / "Newsreader[opsz,wght].ttf"), size)
        f.set_variation_by_axes([min(72, max(6, size)), int(kind[5:])])
    else:
        f = ImageFont.truetype(str(FONTS / "DMMono-Medium.ttf"), size)
    return f


def canvas():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def tracked_w(d, s, f, tr):
    return sum(d.textlength(c, font=f) for c in s) + tr * f.size * max(0, len(s) - 1)


def draw_tracked(d, xy, s, f, fill, tr):
    x, y = xy
    for c in s:
        d.text((x, y), c, font=f, fill=fill)
        x += d.textlength(c, font=f) + tr * f.size


def box(d, x0, y0, x1, y1, color, r=3):
    d.rounded_rectangle((round(x0), round(y0), round(x1), round(y1)), radius=r, fill=color)


def caption(words, lit=None, y=1470, size=54):
    """Serif sentence-case phrase on a tight plate. Words [0, lit) are spoken (bright), the rest dim."""
    im = canvas()
    d = ImageDraw.Draw(im)
    f = font("serif400", size)
    toks = words.split()
    lit = len(toks) if lit is None else lit
    sp = d.textlength(" ", font=f)
    widths = [d.textlength(t, font=f) for t in toks]
    total = sum(widths) + sp * (len(toks) - 1)
    asc, desc = f.getmetrics()
    padx, pady = 16, 10
    x = (W - total) / 2
    box(d, x - padx, y, x + total + padx, y + pady * 2 + asc + desc * 0.55, rgba(P["plate"]))
    for i, (t, w) in enumerate(zip(toks, widths)):
        d.text((x, y + pady), t, font=f, fill=rgba(P["text"] if i < lit else P["dim"]))
        x += w + sp
    return im


def keyword(word, size=250, y=100, color=None):
    """Huge serif word. Default colour Ink (light backgrounds); pass rgba(P['text']) for dark ones."""
    im = canvas()
    d = ImageDraw.Draw(im)
    f = font("serif400", size)
    while d.textlength(word, font=f) > W - 2 * 60 and size > 120:
        size -= 10
        f = font("serif400", size)
    d.text(((W - d.textlength(word, font=f)) / 2, y), word, font=f, fill=color or rgba(P["ink"]))
    return im


def date_line(parts, y=70, color=None):
    im = canvas()
    d = ImageDraw.Draw(im)
    f = font("mono500", 24)
    s = " · ".join(p.upper() for p in parts)
    draw_tracked(d, ((W - tracked_w(d, s, f, 0.25)) / 2, y), s, f, color or rgba(P["ink"], 0.75), 0.25)
    return im


def title_stack(line1, line2, y=110, x=SAFE_X):
    """Line 1 bold caps in cream, line 2 serif italic in the accent colour, each on its own plate."""
    im = canvas()
    d = ImageDraw.Draw(im)
    f1, f2 = font("sans800", 92), font("serif-italic", 96)
    padx = 18
    a1, d1 = f1.getmetrics()
    w1 = d.textlength(line1.upper(), font=f1)
    h1 = a1 + d1 * 0.35 + 22
    box(d, x, y, x + w1 + 2 * padx, y + h1, rgba(P["plate"]))
    d.text((x + padx, y + 12), line1.upper(), font=f1, fill=rgba(P["text"]))
    y2 = y + h1 + 8
    a2, d2 = f2.getmetrics()
    w2 = d.textlength(line2, font=f2)
    box(d, x, y2, x + w2 + 2 * padx, y2 + a2 + d2 * 0.5 + 10, rgba(P["plate"]))
    d.text((x + padx, y2 + 4), line2, font=f2, fill=rgba(P["accent"]))
    return im


def pill(text, highlight=None, y=820, size=40):
    """White pill label, e.g. pill('1:16 of raw footage', '1:16'). Highlight span drawn in the plate colour."""
    im = canvas()
    d = ImageDraw.Draw(im)
    fb, fr = font("sans800", size), font("sans600", size)
    pre, hi, post = "", "", text
    if highlight and highlight in text:
        i = text.index(highlight)
        pre, hi, post = text[:i], highlight, text[i + len(highlight):]
    parts = [(pre, fr, P["ink"]), (hi, fb, P["plate"]), (post, fr, P["ink"])]
    total = sum(d.textlength(s, font=f) for s, f, _ in parts)
    asc, desc = fr.getmetrics()
    x = (W - total) / 2
    box(d, x - 22, y, x + total + 22, y + asc + desc * 0.5 + 24, rgba("#FFFFFF"), r=14)
    for s, f, c in parts:
        d.text((x, y + 12), s, font=f, fill=rgba(c))
        x += d.textlength(s, font=f)
    return im


def note_card(label, text, y=220):
    """Cream rounded card with a mono label, a sans line and a round plate-coloured button."""
    im = canvas()
    d = ImageDraw.Draw(im)
    x0, x1 = 64, W - 64
    box(d, x0, y, x1, y + 170, rgba(P["card"], 0.96), r=28)
    draw_tracked(d, (x0 + 40, y + 34), label.upper(), font("mono500", 20), rgba(P["ink"], 0.55), 0.2)
    d.text((x0 + 40, y + 74), text, font=font("sans500", 44), fill=rgba(P["ink"]))
    cx, cy, r = x1 - 80, y + 95, 38
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=rgba(P["plate"]))
    d.line((cx, cy + 16, cx, cy - 16), fill=rgba(P["text"]), width=5)
    d.line((cx - 13, cy - 3, cx, cy - 16, cx + 13, cy - 3), fill=rgba(P["text"]), width=5, joint="curve")
    return im


def lower_third(name, role, y=1470, x=SAFE_X):
    im = canvas()
    d = ImageDraw.Draw(im)
    fn, fr = font("serif400", 64), font("mono500", 22)
    nw, rw = d.textlength(name, font=fn), tracked_w(d, role.upper(), fr, 0.2)
    padx, pady = 26, 16
    x1, y1 = x + 2 * padx + max(nw, rw), y + pady * 2 + 74 + 12 + 26
    box(d, x, y, x1, y1, rgba(P["plate"]))
    d.rectangle((x, y, x + 3, y1), fill=rgba(P["accent"]))
    d.text((x + padx, y + pady), name, font=fn, fill=rgba(P["text"]))
    draw_tracked(d, (x + padx, y + pady + 86), role.upper(), fr, rgba(P["accent"]), 0.2)
    return im


def stack(*layers):
    out = canvas()
    for layer in layers:
        out = Image.alpha_composite(out, layer)
    return out


def demo(palette):
    use_palette(palette)
    out = ROOT / "presets/graphics/demo" / palette
    out.mkdir(parents=True, exist_ok=True)
    frames = {
        "1_keyword": stack(date_line(["16", "10", "October 2026", "Sunshine Coast"]), keyword("BETTER"),
                           caption("Your business is better", lit=3)),
        "2_title_stack": stack(title_stack("Your business", "is better."), caption("than what people can see", lit=5)),
        "3_note_card": stack(note_card("Vale Studio", "One full day, every four weeks."),
                             caption("a month of professional content.", lit=2)),
        "4_lower_third": stack(pill("1 day of filming", "1 day", y=980), lower_third("Harry", "Founder, Vale Studio")),
    }
    for k, im in frames.items():
        im.save(out / f"{k}.png")
    return out


if __name__ == "__main__" and "--demo" in sys.argv:
    for p in PALETTES:
        print("Wrote", demo(p))


# ---------------------------------------------------------------------------
# "Split" style (reference reel 1): graphics panel on top, speaker below,
# spaced mono uppercase captions on the seam. Vale colours: Ink panel, faint Stone grid.
# ---------------------------------------------------------------------------
SEAM = 940  # panel height on 1080x1920; captions sit on this line
SPLIT = {"panel": "#141313", "grid": "#9C8979", "card": "#1C1A19", "cardLine": "#2E2A28",
         "text": "#F4F0EC", "muted": "#BBAEA2", "accent": "#9C8979", "ok": "#8FC1A0"}


def split_panel(height=SEAM, grid=60):
    """Ink panel over the top of the frame with a faint grid."""
    im = canvas()
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, height), fill=rgba(SPLIT["panel"]))
    for x in range(0, W + 1, grid):
        d.line((x, 0, x, height), fill=rgba(SPLIT["grid"], 0.07), width=1)
    for y in range(0, height + 1, grid):
        d.line((0, y, W, y), fill=rgba(SPLIT["grid"], 0.07), width=1)
    return im


def mono_caption(text, y=SEAM, size=42, tracking=0.12):
    """Spaced DM Mono uppercase, centred on the seam, white with a soft dark edge for busy footage."""
    from PIL import ImageFilter
    s = text.upper()
    im = canvas()
    shadow = canvas()
    d, ds = ImageDraw.Draw(im), ImageDraw.Draw(shadow)
    f = font("mono500", size)
    w = tracked_w(d, s, f, tracking)
    asc, _ = f.getmetrics()
    x, yy = (W - w) / 2, y - asc * 0.62
    draw_tracked(ds, (x, yy), s, f, rgba(SPLIT["panel"], 0.85), tracking)
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    draw_tracked(d, (x, yy), s, f, rgba("#FFFFFF"), tracking)
    return Image.alpha_composite(shadow, im)


def ui_title(word, sub=None, y=330):
    """Big Hanken ExtraBold title in the panel, optional mono sub-line."""
    im = canvas()
    d = ImageDraw.Draw(im)
    size = 150
    f = font("sans800", size)
    while d.textlength(word.upper(), font=f) > W - 160 and size > 70:
        size -= 6
        f = font("sans800", size)
    d.text(((W - d.textlength(word.upper(), font=f)) / 2, y), word.upper(), font=f, fill=rgba(SPLIT["text"]))
    if sub:
        fs = font("mono500", 26)
        s = sub.upper()
        draw_tracked(d, ((W - tracked_w(d, s, fs, 0.2)) / 2, y + size + 40), s, fs, rgba(SPLIT["muted"]), 0.2)
    return im


def checklist(items, tag=None, y=170):
    """Stacked dark cards with a Stone icon tile, a label, a mono sub and a check, like an app list."""
    im = canvas()
    d = ImageDraw.Draw(im)
    x0, x1, h, gap = 150, W - 150, 132, 22
    if tag:
        fs = font("mono500", 24)
        draw_tracked(d, (x0, y - 56), tag.upper(), fs, rgba(SPLIT["muted"]), 0.2)
    for i, (label, sub) in enumerate(items):
        top = y + i * (h + gap)
        box(d, x0, top, x1, top + h, rgba(SPLIT["card"]), r=22)
        d.rounded_rectangle((x0, top, x1, top + h), radius=22, outline=rgba(SPLIT["cardLine"]), width=2)
        box(d, x0 + 28, top + 28, x0 + 104, top + 104, rgba(SPLIT["accent"]), r=18)
        d.text((x0 + 52, top + 38), label[:1].upper(), font=font("sans800", 48), fill=rgba(SPLIT["panel"]))
        d.text((x0 + 132, top + 30), label, font=font("sans600", 42), fill=rgba(SPLIT["text"]))
        draw_tracked(d, (x0 + 132, top + 84), sub.upper(), font("mono500", 20), rgba(SPLIT["muted"]), 0.15)
        cx, cy, r = x1 - 64, top + h / 2, 26
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=rgba(SPLIT["ok"]))
        d.line((cx - 11, cy + 1, cx - 3, cy + 9, cx + 12, cy - 8), fill=rgba(SPLIT["panel"]), width=6, joint="curve")
    return im


def id_card(name, role, place, y=250):
    """Wordmark-style identity block for the panel."""
    im = canvas()
    d = ImageDraw.Draw(im)
    f1 = font("serif400", 132)
    d.text(((W - d.textlength("Vale Studio", font=f1)) / 2, y), "Vale Studio", font=f1, fill=rgba(SPLIT["text"]))
    fs = font("mono500", 26)
    line = f"{name} · {role} · {place}".upper()
    draw_tracked(d, ((W - tracked_w(d, line, fs, 0.2)) / 2, y + 190), line, fs, rgba(SPLIT["muted"]), 0.2)
    d.line(((W - 120) / 2, y + 168, (W + 120) / 2, y + 168), fill=rgba(SPLIT["accent"]), width=2)
    return im


# ---------------------------------------------------------------------------
# "Bold" style (reference reel 2): punchy 1-3 word uppercase captions in heavy sans,
# white on an Ink block, numbered list markers, screen recordings in the top half.
# ---------------------------------------------------------------------------
def bold_caption(text, y=1180, size=78, plate=True):
    """Heavy Hanken uppercase, 1-3 words. Ink block behind by default; plate=False gives a soft shadow."""
    from PIL import ImageFilter
    s = text.upper()
    im = canvas()
    d = ImageDraw.Draw(im)
    f = font("sans800", size)
    w = d.textlength(s, font=f)
    asc, desc = f.getmetrics()
    x = (W - w) / 2
    if plate:
        box(d, x - 18, y, x + w + 18, y + asc + desc * 0.3 + 18, rgba("#141313"), r=6)
        d.text((x, y + 8), s, font=f, fill=rgba("#FFFFFF"))
        return im
    sh = canvas()
    ImageDraw.Draw(sh).text((x, y + 8), s, font=f, fill=rgba("#141313", 0.9))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    d.text((x, y + 8), s, font=f, fill=rgba("#FFFFFF"))
    return Image.alpha_composite(sh, im)


def list_marker(n, y=860, x=None):
    """Numbered beat marker like '#4' in Newsreader italic, cream."""
    im = canvas()
    d = ImageDraw.Draw(im)
    f = font("serif-italic", 150)
    s = f"#{n}"
    w = d.textlength(s, font=f)
    d.text(((W - w) / 2 if x is None else x, y), s, font=f, fill=rgba("#F4F0EC"))
    return im


# ---------------------------------------------------------------------------
# "Noske" style (Tom Noske reels Defg87-BF9r, DeXygzfBUta): 1-2 word bold lowercase captions in warm
# cream, full-screen word cards (dark Ink / light Paper), kinetic stacked cards, quote cards.
# Vale mapping: his #141B1E -> Ink #141313, his #F5F7FD -> Paper warm #F4F0EC, his teal #1C3838 -> Umber
# #5A504A, his peach caption #E0C0AC -> Vale cream #F1E4D6.
# ---------------------------------------------------------------------------
NOSKE = {"dark": "#141313", "light": "#F4F0EC", "onDark": "#F4F0EC", "onLight": "#5A504A",
         "caption": "#F1E4D6", "ghost": 0.38, "quote": "#C9BFB5"}


def noske_caption(text, y_center=1170, size=96, color=None, shadow=None):
    """1-2 words, Hanken Bold, lowercase, warm cream, soft Ink shadow, centred on y_center.
    For light footage pass color=Ink and shadow=white for a soft white glow instead."""
    from PIL import ImageFilter
    s = text.lower().strip(",")
    f = font("sans700", size)
    im, sh = canvas(), canvas()
    d = ImageDraw.Draw(im)
    w = d.textlength(s, font=f)
    while w > W - 120 and size > 60:
        size -= 6
        f = font("sans700", size)
        w = d.textlength(s, font=f)
    asc, _ = f.getmetrics()
    xy = ((W - w) / 2, y_center - asc * 0.6)
    ImageDraw.Draw(sh).text(xy, s, font=f, fill=rgba(shadow or NOSKE["dark"], 0.55))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    d.text(xy, s, font=f, fill=rgba(color or NOSKE["caption"]))
    return Image.alpha_composite(sh, im)


def word_card(text, dark=True, ghost=None, size=132):
    """Full-screen card. ghost: earlier words shown small and faded above the main word (kinetic stack)."""
    bg, fg = (NOSKE["dark"], NOSKE["onDark"]) if dark else (NOSKE["light"], NOSKE["onLight"])
    im = Image.new("RGBA", (W, H), rgba(bg))
    d = ImageDraw.Draw(im)
    s = text.lower()
    f = font("sans700", size)
    while d.textlength(s, font=f) > W - 160 and size > 60:
        size -= 6
        f = font("sans700", size)
    asc, desc = f.getmetrics()
    y = H / 2 - asc * 0.6
    if ghost:
        fg_small = font("sans600", round(size * 0.48))
        gs = ghost.lower()
        d.text(((W - d.textlength(gs, font=fg_small)) / 2, y - fg_small.size * 1.5), gs, font=fg_small,
               fill=rgba(fg, NOSKE["ghost"] + 0.25))
    d.text(((W - d.textlength(s, font=f)) / 2, y), s, font=f, fill=rgba(fg))
    return im


def quote_card(text, dark=False, size=112):
    """Light card with big pale quote marks around a word or short phrase."""
    im = word_card(text, dark=dark, size=size)
    d = ImageDraw.Draw(im)
    q = font("serif400", 300)
    col = rgba(NOSKE["quote"], 0.9)
    d.text((110, H / 2 - 400), "“", font=q, fill=col)
    d.text((W - 110 - d.textlength("”", font=q), H / 2 + 70), "”", font=q, fill=col)
    return im


# ---------------------------------------------------------------------------
# Shared helpers for the white-canvas and glass styles
# ---------------------------------------------------------------------------
def hand_font(size, weight=600):
    f = ImageFont.truetype(str(FONTS / "Caveat[wght].ttf"), size)
    f.set_variation_by_axes([weight])
    return f


def soft_shadow(size_wh, radius, blur=28, alpha=0.18, offset=(0, 18)):
    from PIL import ImageFilter
    w, h = size_wh
    pad = blur * 3
    sh = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad, pad + w, pad + h), radius=radius, fill=rgba("#141313", alpha))
    return sh.filter(ImageFilter.GaussianBlur(blur)), pad, offset


def rounded_mask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=255)
    return m


def tiny_caption(text, y_center, dark=False, size=40):
    """Gannon-style: tiny bold lowercase, white on picture or ink on white."""
    s = text.lower().strip(",.")
    im = canvas()
    d = ImageDraw.Draw(im)
    f = font("sans700", size)
    w = d.textlength(s, font=f)
    asc, _ = f.getmetrics()
    d.text(((W - w) / 2, y_center - asc * 0.6), s, font=f, fill=rgba("#141313" if dark else "#FFFFFF"))
    return im


# ---------------------------------------------------------------------------
# "Gannon" style (Gannon Meyer reel DeNVzrvsDyv): white canvas, floating screen cards with soft shadows,
# handwritten notes and arrows, white top panel split, tiny captions on the seam.
# ---------------------------------------------------------------------------
GANNON = {"canvas": "#FCFAF8", "ink": "#141313", "note": "#5A504A", "accent": "#C0682E", "seam": 884}


def white_panel(height=GANNON["seam"]):
    im = canvas()
    ImageDraw.Draw(im).rectangle((0, 0, W, height), fill=rgba(GANNON["canvas"]))
    return im


def doc_card(title, lines, y=150, x=110, w=860):
    """A floating document/screenshot card: white sheet, soft shadow, bold title, ruled lines with a highlight."""
    im = canvas()
    h = 120 + 72 * len(lines)
    sh, pad, off = soft_shadow((w, h), 22)
    im.alpha_composite(sh, (x - pad + off[0], y - pad + off[1]))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x, y, x + w, y + h), radius=22, fill=rgba("#FFFFFF"), outline=rgba("#E3DDD7"), width=2)
    d.text((x + 44, y + 38), title, font=font("sans700", 40), fill=rgba(GANNON["ink"]))
    for i, (txt, hi) in enumerate(lines):
        ly = y + 116 + i * 72
        if hi:
            d.rounded_rectangle((x + 36, ly - 8, x + 44 + d.textlength(txt, font=font("sans500", 32)) + 16, ly + 44),
                                radius=8, fill=rgba("#F6ECDA"))
        d.text((x + 44, ly), txt, font=font("sans500", 32), fill=rgba("#5A504A"))
    return im


def hand_note(text, x, y, arrow_to=None, size=64, color=None):
    """Handwritten note with an optional curved arrow pointing at arrow_to (x, y)."""
    im = canvas()
    d = ImageDraw.Draw(im)
    col = rgba(color or GANNON["note"])
    d.text((x, y), text, font=hand_font(size), fill=col)
    if arrow_to:
        tw = d.textlength(text, font=hand_font(size))
        sx, sy = x + tw + 16, y + size * 0.55
        ex, ey = arrow_to
        mx, my = (sx + ex) / 2, min(sy, ey) - 80
        pts = [((1 - t) ** 2 * sx + 2 * (1 - t) * t * mx + t ** 2 * ex, (1 - t) ** 2 * sy + 2 * (1 - t) * t * my + t ** 2 * ey)
               for t in [i / 24 for i in range(25)]]
        d.line(pts, fill=col, width=5, joint="curve")
        import math
        ang = math.atan2(ey - pts[-3][1], ex - pts[-3][0])
        for da in (2.6, -2.6):
            d.line((ex, ey, ex + 28 * math.cos(ang + da), ey + 28 * math.sin(ang + da)), fill=col, width=5)
    return im


def asterisk(x, y, r=34, color=None):
    """Small sun/asterisk mark, a nod to the Vale logo sun."""
    import math
    im = canvas()
    d = ImageDraw.Draw(im)
    col = rgba(color or GANNON["accent"])
    for k in range(8):
        a = k * math.pi / 4
        d.line((x, y, x + r * math.cos(a), y + r * math.sin(a)), fill=col, width=9)
    return im


# ---------------------------------------------------------------------------
# "Remy" style (Remy reel DeeroIoRpnr): bright and natural, light top panel with UI mockup cards or
# a photo collage, a sticker label, small white captions.
# ---------------------------------------------------------------------------
REMY = {"panel": "#F4F0EC", "card": "#FFFFFF", "bar": "#E3DDD7", "chip": "#5A504A", "seam": 880}


def light_panel(height=REMY["seam"]):
    im = canvas()
    ImageDraw.Draw(im).rectangle((0, 0, W, height), fill=rgba(REMY["panel"]))
    return im


def ui_mock(cards, y=170):
    """Row of white UI cards with grey text bars; one bar per card can be a dark chip with a label."""
    im = canvas()
    d = ImageDraw.Draw(im)
    n = len(cards)
    gap, x0 = 28, 70
    w = (W - 2 * x0 - gap * (n - 1)) / n
    for i, (title, chip) in enumerate(cards):
        x = x0 + i * (w + gap)
        sh, pad, off = soft_shadow((int(w), 520), 20, blur=20, alpha=0.12, offset=(0, 10))
        im.alpha_composite(sh, (int(x - pad), int(y - pad + 10)))
        d.rounded_rectangle((x, y, x + w, y + 520), radius=20, fill=rgba(REMY["card"]))
        d.text((x + 28, y + 30), title, font=font("sans700", 34), fill=rgba("#141313"))
        for j in range(4):
            d.rounded_rectangle((x + 28, y + 100 + j * 62, x + w - 28 - (j % 2) * 60, y + 126 + j * 62), radius=13,
                                fill=rgba(REMY["bar"]))
        if chip:
            f = font("sans700", 28)
            d.rounded_rectangle((x + 28, y + 400, x + 28 + d.textlength(chip, font=f) + 36, y + 456), radius=28,
                                fill=rgba(REMY["chip"]))
            d.text((x + 46, y + 410), chip, font=f, fill=rgba("#F4F0EC"))
    return im


def sticker(word, tag, x=110, y=140):
    """'SKILL of the week' style sticker: bold caps word, handwritten tag on a tilted Umber strip."""
    im = canvas()
    d = ImageDraw.Draw(im)
    f = font("sans800", 120)
    d.text((x, y), word.upper(), font=f, fill=rgba("#FFFFFF"), stroke_width=6, stroke_fill=rgba("#141313", 0.35))
    tag_im = Image.new("RGBA", (700, 140), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag_im)
    hf = hand_font(72, 700)
    tw = td.textlength(tag, font=hf)
    td.rounded_rectangle((0, 20, tw + 48, 120), radius=10, fill=rgba("#5A504A"))
    td.text((24, 22), tag, font=hf, fill=rgba("#F4F0EC"))
    tag_im = tag_im.rotate(-4, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(tag_im, (x + 60, y + 128))
    return im


# ---------------------------------------------------------------------------
# "JayanT" style (JayanT reel DeY97HPFWBP): motion-design inserts, dark glass UI cards on black,
# big stat numbers, check lists, small mono labels. Vale: Ink ground, warm Stone accents, no light streak.
# ---------------------------------------------------------------------------
GLASS = {"ground": "#0E0D0D", "card": "#1C1A19", "line": "#34302D", "text": "#F4F0EC", "muted": "#948A82",
         "accent": "#C9A27E", "ok": "#8FC1A0"}


def glass_stat(number, label, sub=None, highlight=False):
    """Full-screen insert: one glass card with a big number. highlight=True uses the warm accent card."""
    im = Image.new("RGBA", (W, H), rgba(GLASS["ground"]))
    d = ImageDraw.Draw(im)
    x0, x1, y0, y1 = 110, W - 110, 760, 1160
    fill = rgba("#2B241E") if highlight else rgba(GLASS["card"])
    d.rounded_rectangle((x0, y0, x1, y1), radius=36, fill=fill, outline=rgba(GLASS["line"]), width=2)
    draw_tracked(d, (x0 + 56, y0 + 52), label.upper(), font("mono500", 26), rgba(GLASS["muted"]), 0.2)
    d.text((x0 + 50, y0 + 110), number, font=font("sans800", 190), fill=rgba(GLASS["accent"] if highlight else GLASS["text"]))
    if sub:
        d.text((x0 + 56, y1 - 80), sub, font=font("sans500", 34), fill=rgba(GLASS["muted"]))
    return im


def glass_list(title, items, checked=True):
    """Full-screen insert: glass card with a title and a ticked list."""
    im = Image.new("RGBA", (W, H), rgba(GLASS["ground"]))
    d = ImageDraw.Draw(im)
    x0, x1 = 110, W - 110
    h = 150 + 96 * len(items)
    y0 = (H - h) / 2
    d.rounded_rectangle((x0, y0, x1, y0 + h), radius=36, fill=rgba(GLASS["card"]), outline=rgba(GLASS["line"]), width=2)
    draw_tracked(d, (x0 + 56, y0 + 52), title.upper(), font("mono500", 26), rgba(GLASS["muted"]), 0.2)
    for i, it in enumerate(items):
        yy = y0 + 120 + i * 96
        d.line((x0 + 56, yy - 14, x1 - 56, yy - 14), fill=rgba(GLASS["line"]), width=2)
        d.text((x0 + 56, yy + 6), it, font=font("sans600", 44), fill=rgba(GLASS["text"]))
        if checked:
            cx, cy = x1 - 90, yy + 34
            d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=rgba(GLASS["ok"]))
            d.line((cx - 10, cy, cx - 3, cy + 8, cx + 11, cy - 7), fill=rgba(GLASS["ground"]), width=5, joint="curve")
    return im


def mono_word_card(text):
    """Full-screen black card with spaced mono caps, e.g. 'SAME  ACCOUNT'."""
    im = Image.new("RGBA", (W, H), rgba(GLASS["ground"]))
    d = ImageDraw.Draw(im)
    f = font("mono500", 54)
    s = text.upper()
    draw_tracked(d, ((W - tracked_w(d, s, f, 0.3)) / 2, H / 2 - 30), s, f, rgba(GLASS["text"]), 0.3)
    return im


def types_board(title, items, active, y=110):
    """Gannon-simple board for the white panel: a handwritten title and numbered rows.
    items: [(name, note)]. Rows before `active` are done (ticked), `active` is highlighted, later rows are faint."""
    im = canvas()
    d = ImageDraw.Draw(im)
    d.text((110, y), title, font=hand_font(78, 600), fill=rgba(GANNON["note"]))
    row_h, x0, x1 = 150, 90, W - 90
    for i, (name, note) in enumerate(items):
        top = y + 150 + i * row_h
        state = "done" if i < active else ("active" if i == active else "todo")
        if state == "active":
            sh, pad, off = soft_shadow((x1 - x0, row_h - 22), 24, blur=22, alpha=0.16, offset=(0, 12))
            im.alpha_composite(sh, (x0 - pad, top - pad + 12))
            d = ImageDraw.Draw(im)
            d.rounded_rectangle((x0, top, x1, top + row_h - 22), radius=24, fill=rgba("#FFFFFF"), outline=rgba("#E3DDD7"), width=2)
        a = 1.0 if state != "todo" else 0.28
        num = f"{i + 1:02d}"
        draw_tracked(d, (x0 + 34, top + 44), num, font("mono500", 30), rgba("#9C8979", a), 0.1)
        d.text((x0 + 120, top + 22), name, font=font("sans700", 56), fill=rgba("#141313", a))
        if state != "todo":
            d.text((x0 + 122, top + 86), note, font=font("sans500", 28), fill=rgba("#5A504A", 0.85 * a))
        if state == "done":
            cx, cy = x1 - 60, top + 60
            d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=rgba("#5A504A"))
            d.line((cx - 10, cy, cx - 3, cy + 8, cx + 11, cy - 7), fill=rgba("#F4F0EC"), width=5, joint="curve")
    return im
