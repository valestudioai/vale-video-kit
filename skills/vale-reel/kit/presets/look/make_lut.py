"""Generate the Vale Studio look as a 33-point .cube LUT (Rec.709 in, Rec.709 out).

Direction (brand/BRAND.md > Colour grade, references/NOTES.md reel 3):
warm and natural, soft contrast, blacks lifted slightly toward umber, highlights rolled off,
greens/cyans/blues pulled back so the warm neutrals lead, skin left alone.

Run: ~/.cache/video-editor/whisperx-venv/bin/python presets/look/make_lut.py
"""
from pathlib import Path

import numpy as np

N = 33
OUT = Path(__file__).with_name("Vale_Warm_Natural.cube")

# Tunable strengths
WARM_R, WARM_B = 1.025, 0.955       # white balance nudge toward warm
LIFT = 0.035                          # how far blacks lift
LIFT_TINT = np.array([0.090, 0.078, 0.071])  # umber-ish shadow tint (#5A504A relative)
SHOULDER = 0.82                       # highlights above this roll off
CONTRAST = 0.10                       # gentle midtone S-curve amount
GLOBAL_SAT = 0.94
CYAN_BLUE_SAT = 0.58                  # 160-250 deg (backdrops, skies)
GREEN_SAT = 0.80                      # 80-160 deg (foliage)
CYAN_WARM_SHIFT = -4.0                 # negative pulls cyans toward blue-grey, away from mint


def rgb_to_hsv(c):
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    mx, mn = c.max(-1), c.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rm, gm, bm = m & (mx == r), m & (mx == g) & (mx != r), m & (mx == b) & (mx != r) & (mx != g)
    h[rm] = ((g - b)[rm] / d[rm]) % 6
    h[gm] = (b - r)[gm] / d[gm] + 2
    h[bm] = (r - g)[bm] / d[bm] + 4
    h = h * 60.0
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    return h, s, mx


def hsv_to_rgb(h, s, v):
    h = (h % 360) / 60.0
    i = np.floor(h).astype(int) % 6
    f = h - np.floor(h)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    out = np.stack([v, t, p], -1)
    for k, (a, b_, c) in enumerate([(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]):
        sel = i == k
        out[sel] = np.stack([a[sel], b_[sel], c[sel]], -1)
    return out


def band(h, lo, hi, feather=20.0):
    """1 inside [lo, hi] degrees, smooth falloff over `feather` degrees outside."""
    up = np.clip((h - (lo - feather)) / feather, 0, 1)
    down = np.clip(((hi + feather) - h) / feather, 0, 1)
    return np.minimum(up, down)


def grade(rgb):
    c = rgb.copy()
    # 1. warm white balance
    c[..., 0] *= WARM_R
    c[..., 2] *= WARM_B
    # 2. hue-selective saturation (leave skin 0-50 deg untouched)
    h, s, v = rgb_to_hsv(np.clip(c, 0, 1))
    cb = band(h, 160, 250)
    gr = band(h, 80, 160)
    s = s * GLOBAL_SAT * (1 - cb * (1 - CYAN_BLUE_SAT)) * (1 - gr * (1 - GREEN_SAT))
    h = h - cb * CYAN_WARM_SHIFT
    c = hsv_to_rgb(h, np.clip(s, 0, 1), v)
    # 3. gentle S-curve on luma-ish values
    c = np.clip(c, 0, 1)
    c = (1 - 2 * CONTRAST) * c + 2 * CONTRAST * (c * c * (3 - 2 * c))
    # 4. highlight shoulder: above SHOULDER, ease into 1.0 instead of clipping
    k = 1.6
    over = np.maximum(c - SHOULDER, 0) / (1 - SHOULDER)
    c = np.where(c > SHOULDER, SHOULDER + (1 - SHOULDER) * (1 - np.exp(-k * over)) / (1 - np.exp(-k)), c)
    # 5. lift blacks toward umber (black maps to a dark warm grey, white stays white)
    lift = LIFT * LIFT_TINT / LIFT_TINT.mean()
    c = c + lift * (1 - c)
    return np.clip(c, 0, 1)


def main():
    grid = np.linspace(0, 1, N)
    b, g, r = np.meshgrid(grid, grid, grid, indexing="ij")  # .cube order: red changes fastest
    rgb = np.stack([r, g, b], -1).reshape(-1, 3)
    out = grade(rgb)
    lines = ['TITLE "Vale Warm Natural"', "# Vale Studio look v1. Rec.709 to Rec.709. Apply after exposure and white balance are correct.",
             f"LUT_3D_SIZE {N}", "DOMAIN_MIN 0.0 0.0 0.0", "DOMAIN_MAX 1.0 1.0 1.0"]
    lines += [f"{x:.6f} {y:.6f} {z:.6f}" for x, y, z in out]
    OUT.write_text("\n".join(lines) + "\n")
    print(f"Wrote {OUT} ({N}^3)")


if __name__ == "__main__":
    main()
