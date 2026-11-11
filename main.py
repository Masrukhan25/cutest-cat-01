#!/usr/bin/env python3
"""Draw the cutest cat (make.fun bounty cutest-cat-01).

A program that draws one picture of a cat and writes it to /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png outside the grader). Deterministic: no
randomness, no network, no time, no input.

Standard library only (no Pillow): a small software rasterizer draws the
shapes into a byte buffer and a pure-Python PNG encoder (zlib) writes it.
Two runs write the same bytes.

The cat: a ginger kitten, sitting, head tilted 6 degrees, big bright eyes,
pink nose, blush cheeks, whiskers, curled tail, and a pink yarn ball at
its paw.
"""
import math
import os
import struct
import zlib

W = 1024
H = 1024

# Palette (soft, warm, storybook)
BG = (255, 243, 222)
GINGER = (244, 164, 96)
GINGER_DARK = (232, 138, 68)
GINGER_LIGHT = (255, 205, 150)
CREAM = (255, 240, 214)
PINK = (255, 150, 168)
PINK_DARK = (235, 110, 135)
BLUSH = (255, 140, 150)
DARK = (74, 52, 42)
EYE = (64, 42, 32)
WHITE = (255, 255, 255)
YARN = (255, 120, 150)
YARN_DARK = (225, 80, 115)
IRIS = (150, 95, 45)


class Canvas:
    """An RGB pixel buffer with a few filled-shape primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(bg) * (w * h))

    def _span(self, y, x0, x1, color):
        """Fill the horizontal span [x0, x1] on row y with color."""
        if y < 0 or y >= self.h:
            return
        x0 = max(0, int(math.floor(x0)))
        x1 = min(self.w - 1, int(math.ceil(x1)))
        if x1 < x0:
            return
        n = x1 - x0 + 1
        start = (y * self.w + x0) * 3
        self.buf[start:start + n * 3] = bytes(color) * n

    def _dot(self, x, y, color, r):
        """A filled disc of radius r centred on (x, y)."""
        self.fill_ellipse(x, y, r, r, color)

    def fill_ellipse(self, cx, cy, rx, ry, color):
        """Filled ellipse centred on (cx, cy) with radii rx, ry."""
        rx = float(rx)
        ry = float(ry)
        if rx <= 0 or ry <= 0:
            return
        y0 = max(0, int(math.floor(cy - ry)))
        y1 = min(self.h - 1, int(math.ceil(cy + ry)))
        for y in range(y0, y1 + 1):
            dy = (y - cy) / ry
            if abs(dy) >= 1:
                continue
            dx = rx * math.sqrt(1 - dy * dy)
            self._span(y, cx - dx, cx + dx, color)

    def ellipse(self, cx, cy, rx, ry, fill, outline=None, width=1):
        """Filled ellipse, optionally with an outline (drawn as a larger
        ellipse underneath, which reads as a border of `width` px)."""
        if outline is not None and width > 0:
            self.fill_ellipse(cx, cy, rx + width, ry + width, outline)
        if fill is not None:
            self.fill_ellipse(cx, cy, rx, ry, fill)

    def polygon(self, points, fill, outline=None):
        """Filled polygon; an outline is drawn as lines along the edges."""
        if fill is not None:
            self._fill_polygon(points, fill)
        if outline is not None:
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                self.line(x0, y0, x1, y1, outline, 3)

    def _fill_polygon(self, points, color):
        """Scanline fill of a polygon."""
        ys = [p[1] for p in points]
        y0 = max(0, int(math.floor(min(ys))))
        y1 = min(self.h - 1, int(math.ceil(max(ys))))
        n = len(points)
        for y in range(y0, y1 + 1):
            xs = []
            for i in range(n):
                x0, y0p = points[i]
                x1, y1p = points[(i + 1) % n]
                if (y0p <= y < y1p) or (y1p <= y < y0p):
                    if y1p != y0p:
                        xs.append(x0 + (y - y0p) * (x1 - x0) / (y1p - y0p))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self._span(y, xs[i], xs[i + 1], color)

    def line(self, x0, y0, x1, y1, color, width=1):
        """A thick line: stepped discs along the segment."""
        dx = x1 - x0
        dy = y1 - y0
        dist = math.hypot(dx, dy)
        steps = max(1, int(dist / max(1.0, width * 0.5)) + 1)
        r = width / 2.0
        for i in range(steps + 1):
            t = i / steps
            self._dot(x0 + dx * t, y0 + dy * t, color, r)

    def arc(self, cx, cy, rx, ry, start_deg, end_deg, color, width=1):
        """An arc (degrees, 0 = east, going clockwise as y grows)."""
        a0 = math.radians(start_deg)
        a1 = math.radians(end_deg)
        if a1 <= a0:
            a1 += 2 * math.pi
        span = a1 - a0
        steps = max(4, int(span * max(rx, ry) / max(1.0, width * 0.5)) + 1)
        r = width / 2.0
        for i in range(steps + 1):
            a = a0 + span * i / steps
            x = cx + rx * math.cos(a)
            y = cy + ry * math.sin(a)
            self._dot(x, y, color, r)

    def save_png(self, path):
        """Write the buffer as a 24-bit RGB PNG (filter 0, zlib)."""
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)
            raw += self.buf[y * stride:(y + 1) * stride]
        comp = zlib.compress(bytes(raw), 6)

        def chunk(ctype, data):
            c = struct.pack(">I", len(data)) + ctype + data
            c += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
            return c

        png = b"\x89PNG\r\n\x1a\n"
        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        png += chunk(b"IHDR", ihdr)
        png += chunk(b"IDAT", comp)
        png += chunk(b"IEND", b"")
        with open(path, "wb") as f:
            f.write(png)


def rot(x, y, cx, cy, deg):
    """Rotate point (x, y) around (cx, cy) by deg degrees (clockwise as y grows)."""
    a = math.radians(deg)
    dx = x - cx
    dy = y - cy
    ca = math.cos(a)
    sa = math.sin(a)
    return (cx + dx * ca - dy * sa, cy + dx * sa + dy * ca)


def main():
    img = Canvas(W, H, BG)
    cx = W * 0.50  # cat centre x

    # ---- tail: a curled tube hugging the body's right side (behind the body) ----
    tx, ty, trx, try_ = cx + 180, H * 0.76, 70, 140
    img.arc(tx, ty, trx, try_, 250, 110, GINGER_DARK, 23)
    img.arc(tx, ty, trx, try_, 250, 110, GINGER, 19)
    img.arc(tx, ty, trx, try_, 250, 292, CREAM, 19)
    img.arc(tx, ty, trx, try_, 330, 20, GINGER_DARK, 3)

    # ---- body: sitting, rounded, tall enough to meet the head ----
    img.ellipse(cx, H * 0.71, 178, 194, GINGER, GINGER_DARK, 2)
    # belly (cream)
    img.ellipse(cx, H * 0.76, 108, 144, CREAM)

    # ---- front paws: two small paws together at the front ----
    for sx in (-1, 1):
        px = cx + sx * 52
        img.ellipse(px, H * 0.8675, 42, 48, GINGER, GINGER_DARK, 2)
        img.line(px - 14, H * 0.855, px - 14, H * 0.905, GINGER_DARK, 3)
        img.line(px + 14, H * 0.855, px + 14, H * 0.905, GINGER_DARK, 3)

    # ---- yarn ball (favourite toy) at the left paw ----
    yx, yy, yr = cx - 238, H * 0.835, 60
    img.ellipse(yx, yy, yr, yr, YARN, YARN_DARK, 2)
    img.arc(yx, yy, yr, yr, 20, 160, YARN_DARK, 5)
    img.arc(yx, yy, yr * 0.7, yr * 0.7, 200, 340, YARN_DARK, 5)
    img.arc(yx, yy, yr * 0.45, yr * 0.45, 100, 260, YARN_DARK, 4)
    # loose strand from the ball to the paw
    img.arc((yx + 10 + cx - 70) / 2, yy + 20, (cx - 70 - yx - 10) / 2, 40, 300, 80, YARN_DARK, 5)

    # ---- head: big and round, tilted 6 degrees, overlapping the body ----
    hx, hy = cx, H * 0.40
    hr = 185
    TILT = 6.0

    def R(x, y):
        return rot(x, y, hx, hy, TILT)

    # ears (behind the head circle)
    for sx in (-1, 1):
        ex = hx + sx * 118
        ey = hy - 128
        outer = [R(ex - 62, ey + 78), R(ex + sx * 18, ey - 62), R(ex + 78, ey + 62)]
        img.polygon(outer, GINGER, GINGER_DARK)
        inner = [R(ex - 32, ey + 58), R(ex + sx * 12, ey - 28), R(ex + 44, ey + 48)]
        img.polygon(inner, PINK)
    # head circle
    img.ellipse(hx, hy, hr, hr, GINGER, GINGER_DARK, 3)
    # forehead stripes
    for sx in (-1, 0, 1):
        sxp, syp = R(hx + sx * 42, hy - hr + 43)
        img.arc(sxp, syp, 16, 35, 270 + TILT, 90 + TILT, GINGER_DARK, 6)
    # muzzle (cream)
    mx, my = R(hx, hy + 78)
    img.ellipse(mx, my, 95, 50, CREAM)
    # eyes: very large, bright, looking slightly up
    for sx in (-1, 1):
        ex, ey = R(hx + sx * 78, hy - 18)
        er = 44
        img.ellipse(ex, ey, er, er, WHITE, DARK, 2)
        img.ellipse(ex, ey + 4, 30, 30, IRIS)
        img.ellipse(ex, ey + 4, 16, 16, EYE)
        img.ellipse(ex - 11, ey - 17, 9, 9, WHITE)
        img.ellipse(ex + 13, ey + 13, 5, 5, WHITE)
    # blush
    for sx in (-1, 1):
        bx, by = R(hx + sx * 128, hy + 52)
        img.ellipse(bx, by, 30, 18, BLUSH)
    # nose: small pink triangle
    nose = [R(hx - 20, hy + 48), R(hx + 20, hy + 48), R(hx, hy + 72)]
    img.polygon(nose, PINK, PINK_DARK)
    # mouth: tiny "w"
    m1x, m1y = R(hx - 17, hy + 85)
    img.arc(m1x, m1y, 17, 19, TILT, 180 + TILT, DARK, 4)
    m2x, m2y = R(hx + 17, hy + 85)
    img.arc(m2x, m2y, 17, 19, TILT, 180 + TILT, DARK, 4)
    # whiskers
    for sx in (-1, 1):
        for wy, ang in ((hy + 30, -8), (hy + 52, 0), (hy + 74, 8)):
            x0, y0 = R(hx + sx * 88, wy)
            x1, y1 = R(hx + sx * 168, wy + ang)
            img.line(x0, y0, x1, y1, DARK, 3)

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "entry.png")
    img.save_png(out)
    print(out)


if __name__ == "__main__":
    main()
