#!/usr/bin/env python3
"""Draw the cutest cat (make.fun bounty cutest-cat-01).

A program that draws one picture of a cat and writes it to /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png outside the grader). Deterministic: no
randomness, no network, no time, no input. Pure Pillow drawing, so two runs
write the same bytes.

The cat: a ginger kitten, sitting, head tilted, big bright eyes, pink nose,
blush cheeks, whiskers, curled tail, and a pink yarn ball at its paw.
"""
import os
from PIL import Image, ImageDraw

S = 2  # supersample factor (draw at 2048, downscale to 1024 for smooth edges)
W = 1024 * S
H = 1024 * S

# Palette (soft, warm, storybook)
BG = (255, 243, 222)
GINGER = (244, 164, 96)        # main fur
GINGER_DARK = (232, 138, 68)   # shading / stripes
GINGER_LIGHT = (255, 205, 150)
CREAM = (255, 240, 214)
PINK = (255, 150, 168)         # inner ear / nose / yarn
PINK_DARK = (235, 110, 135)
BLUSH = (255, 140, 150)
DARK = (74, 52, 42)            # outlines / eyes / nose line
EYE = (64, 42, 32)
WHITE = (255, 255, 255)
YARN = (255, 120, 150)
YARN_DARK = (225, 80, 115)


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")

    cx = W * 0.50  # cat centre x

    # ---- tail: a curled tube hugging the body's right side (behind the body) ----
    # arc sweeping the right side (250 -> 0 -> 110); both ends tuck behind the body
    tb = [cx + 110 * S, H * 0.62, cx + 250 * S, H * 0.90]
    d.arc(tb, start=250, end=110, fill=GINGER_DARK, width=46 * S)
    d.arc(tb, start=250, end=110, fill=GINGER, width=38 * S)
    # cream tip: the top stretch of the same arc, same width, so it reads as one tail
    d.arc(tb, start=250, end=292, fill=CREAM, width=38 * S)
    # one tail stripe
    d.arc(tb, start=330, end=20, fill=GINGER_DARK, width=6 * S)

    # ---- body: sitting, rounded, tall enough to meet the head ----
    d.ellipse([cx - 178 * S, H * 0.52, cx + 178 * S, H * 0.90], fill=GINGER)
    d.ellipse([cx - 178 * S, H * 0.52, cx + 178 * S, H * 0.90], outline=GINGER_DARK, width=4 * S)
    # belly (cream)
    d.ellipse([cx - 108 * S, H * 0.62, cx + 108 * S, H * 0.90], fill=CREAM)

    # ---- front paws: two small paws together at the front ----
    for sx in (-1, 1):
        px = cx + sx * 52 * S
        d.ellipse([px - 42 * S, H * 0.82, px + 42 * S, H * 0.915], fill=GINGER)
        d.ellipse([px - 42 * S, H * 0.82, px + 42 * S, H * 0.915], outline=GINGER_DARK, width=3 * S)
        d.line([(px - 14 * S, H * 0.855), (px - 14 * S, H * 0.905)], fill=GINGER_DARK, width=3 * S)
        d.line([(px + 14 * S, H * 0.855), (px + 14 * S, H * 0.905)], fill=GINGER_DARK, width=3 * S)

    # ---- yarn ball (favourite toy) at the left paw ----
    yx, yy, yr = cx - 238 * S, H * 0.835, 60 * S
    d.ellipse([yx - yr, yy - yr, yx + yr, yy + yr], fill=YARN)
    d.ellipse([yx - yr, yy - yr, yx + yr, yy + yr], outline=YARN_DARK, width=4 * S)
    d.arc([yx - yr, yy - yr, yx + yr, yy + yr], start=20, end=160, fill=YARN_DARK, width=5 * S)
    d.arc([yx - yr * 0.7, yy - yr * 0.7, yx + yr * 0.7, yy + yr * 0.7], start=200, end=340, fill=YARN_DARK, width=5 * S)
    d.arc([yx - yr * 0.45, yy - yr * 0.45, yx + yr * 0.45, yy + yr * 0.45], start=100, end=260, fill=YARN_DARK, width=4 * S)
    # loose strand from the ball to the paw
    d.arc([yx + 10 * S, yy - 20 * S, cx - 70 * S, yy + 60 * S], start=300, end=80, fill=YARN_DARK, width=5 * S)

    # ---- head: big and round, tilted slightly (charm), overlapping the body ----
    head = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(head)
    hx, hy = cx, H * 0.40  # head centre (lowered so it meets the body)
    hr = 185 * S           # head radius

    # ears (behind the head circle)
    for sx in (-1, 1):
        ex = hx + sx * 118 * S
        ey = hy - 128 * S
        hd.polygon(
            [(ex - 62 * S, ey + 78 * S), (ex + sx * 18 * S, ey - 62 * S), (ex + 78 * S, ey + 62 * S)],
            fill=GINGER,
        )
        hd.polygon(
            [(ex - 62 * S, ey + 78 * S), (ex + sx * 18 * S, ey - 62 * S), (ex + 78 * S, ey + 62 * S)],
            outline=GINGER_DARK,
        )
        hd.polygon(
            [(ex - 32 * S, ey + 58 * S), (ex + sx * 12 * S, ey - 28 * S), (ex + 44 * S, ey + 48 * S)],
            fill=PINK,
        )
    # head circle
    hd.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=GINGER)
    hd.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], outline=GINGER_DARK, width=5 * S)
    # forehead stripes
    for sx in (-1, 0, 1):
        hd.arc([hx + sx * 42 * S - 16 * S, hy - hr + 8 * S, hx + sx * 42 * S + 16 * S, hy - hr + 78 * S],
               start=270, end=90, fill=GINGER_DARK, width=6 * S)
    # muzzle (cream)
    hd.ellipse([hx - 95 * S, hy + 28 * S, hx + 95 * S, hy + 128 * S], fill=CREAM)
    # eyes: very large, bright, looking slightly up
    for sx in (-1, 1):
        ex = hx + sx * 78 * S
        ey = hy - 18 * S
        er = 44 * S
        hd.ellipse([ex - er, ey - er, ex + er, ey + er], fill=WHITE)
        hd.ellipse([ex - er, ey - er, ex + er, ey + er], outline=DARK, width=4 * S)
        ir = 30 * S
        hd.ellipse([ex - ir, ey - ir + 4 * S, ex + ir, ey + ir + 4 * S], fill=(150, 95, 45))
        pr = 16 * S
        hd.ellipse([ex - pr, ey - pr + 4 * S, ex + pr, ey + pr + 4 * S], fill=EYE)
        hd.ellipse([ex - 20 * S, ey - 26 * S, ex - 2 * S, ey - 8 * S], fill=WHITE)
        hd.ellipse([ex + 8 * S, ey + 8 * S, ex + 18 * S, ey + 18 * S], fill=WHITE)
    # blush
    for sx in (-1, 1):
        bx = hx + sx * 128 * S
        by = hy + 52 * S
        hd.ellipse([bx - 30 * S, by - 18 * S, bx + 30 * S, by + 18 * S], fill=BLUSH + (170,))
    # nose: small pink triangle
    hd.polygon([(hx - 20 * S, hy + 48 * S), (hx + 20 * S, hy + 48 * S), (hx, hy + 72 * S)], fill=PINK)
    hd.polygon([(hx - 20 * S, hy + 48 * S), (hx + 20 * S, hy + 48 * S), (hx, hy + 72 * S)], outline=PINK_DARK)
    # mouth: tiny "w"
    hd.arc([hx - 34 * S, hy + 66 * S, hx, hy + 104 * S], start=0, end=180, fill=DARK, width=4 * S)
    hd.arc([hx, hy + 66 * S, hx + 34 * S, hy + 104 * S], start=0, end=180, fill=DARK, width=4 * S)
    # whiskers
    for sx in (-1, 1):
        for wy, ang in ((hy + 30 * S, -8), (hy + 52 * S, 0), (hy + 74 * S, 8)):
            x0 = hx + sx * 88 * S
            x1 = hx + sx * 168 * S
            y1 = wy + ang * S
            hd.line([(x0, wy), (x1, y1)], fill=DARK + (200,), width=3 * S)

    # tilt the whole head a few degrees (head tilt = charm)
    head = head.rotate(6, resample=Image.BICUBIC, center=(hx, hy))
    img = Image.alpha_composite(img.convert("RGBA"), head).convert("RGB")

    # ---- downscale to 1024 (smooth) and save ----
    img = img.resize((1024, 1024), Image.LANCZOS)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "entry.png")
    img.save(out, "PNG", optimize=True)
    print(out)


if __name__ == "__main__":
    main()
