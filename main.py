#!/usr/bin/env python3
"""Meme Sprint: AI Agents Ship Games.

A classic top-text / bottom-text meme, rendered 1024x1024 with the
Python standard library alone (own PNG encoder, own bitmap font).

The joke, first thing a viewer gets:

  MY AI AGENT SHIPPED MY GAME IN 4 MINUTES
  IT ALSO SHIPPED 3,000 BUGS AND A TODO THAT SAYS 'FIX LATER'

The middle panel shows the agent itself: a cheerful robot at its desk,
laptop open on a finished game, a rocket already launching, and a few
cartoon bugs crawling in underneath.

Fully deterministic: no randomness, no network, no files read at run
time. Two runs write byte-identical files.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKY = (127, 203, 242)
GRASS = (110, 196, 96)
GRASS2 = (86, 170, 76)
SUN = (255, 214, 64)
SILVER = (196, 205, 214)
SILVER_D = (148, 158, 170)
DARK = (43, 52, 66)
RED = (226, 64, 52)
GREEN = (46, 180, 88)
BLUE = (52, 120, 226)
BROWN = (139, 90, 43)
BROWN_D = (110, 70, 32)
PINK = (244, 158, 178)
ORANGE = (255, 140, 40)
YELLOW = (255, 222, 89)
PURPLE = (150, 96, 210)
SCREEN = (24, 44, 84)

buf = bytearray(W * H * 3)


def put(x, y, rgb):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = rgb


def rect(x0, y0, x1, y1, rgb):
    x0 = max(0, int(x0))
    y0 = max(0, int(y0))
    x1 = min(W, int(x1))
    y1 = min(H, int(y1))
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(rgb) * (x1 - x0)
    for y in range(y0, y1):
        i = (y * W + x0) * 3
        buf[i:i + len(row)] = row


def circle(cx, cy, r, rgb):
    cx, cy, r = int(cx), int(cy), int(r)
    r2 = r * r
    for y in range(cy - r, cy + r + 1):
        dy = y - cy
        rem = r2 - dy * dy
        if rem < 0:
            continue
        dx = int(math.sqrt(rem))
        for x in range(cx - dx, cx + dx + 1):
            put(x, y, rgb)


def poly(points, rgb):
    ys = [p[1] for p in points]
    y_lo, y_hi = int(min(ys)), int(max(ys))
    n = len(points)
    for y in range(y_lo, y_hi + 1):
        xs = []
        for k in range(n):
            x0, yy0 = points[k]
            x1, yy1 = points[(k + 1) % n]
            if (yy0 <= y < yy1) or (yy1 <= y < yy0):
                xs.append(x0 + (y - yy0) * (x1 - x0) / (yy1 - yy0))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                put(x, y, rgb)


def thick_line(p, q, wdt, rgb):
    r = wdt / 2.0
    dist = math.hypot(q[0] - p[0], q[1] - p[1])
    steps = max(1, int(dist / (r * 0.6)))
    for s in range(steps + 1):
        t = s / steps
        circle(p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, r, rgb)


# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, one string per row, '1' = filled.
GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}


def draw_text(lines, cx, top, cell, color, outline=BLACK, gap=None):
    """Centered lines of huge bold text with a black outline."""
    if gap is None:
        gap = cell * 2
    line_h = 7 * cell + gap
    o = max(2, cell // 4)
    for li, line in enumerate(lines):
        w = len(line) * 6 * cell - cell
        x = cx - w // 2
        y = top + li * line_h
        # outline pass: every filled cell drawn expanded in outline colour
        for ci, ch in enumerate(line):
            glyph = GLYPHS.get(ch, GLYPHS[" "])
            ox = x + ci * 6 * cell
            for r in range(7):
                row = glyph[r]
                for c in range(5):
                    if row[c] == "1":
                        rect(ox + c * cell - o, y + r * cell - o,
                             ox + (c + 1) * cell + o,
                             y + (r + 1) * cell + o, outline)
        # face pass
        for ci, ch in enumerate(line):
            glyph = GLYPHS.get(ch, GLYPHS[" "])
            ox = x + ci * 6 * cell
            for r in range(7):
                row = glyph[r]
                for c in range(5):
                    if row[c] == "1":
                        rect(ox + c * cell, y + r * cell,
                             ox + (c + 1) * cell, y + (r + 1) * cell, color)


# ---------------------------------------------------------------- scene
def bug(x, y, s):
    """One cartoon bug: round body, head, six legs, antennae."""
    circle(x, y, 13 * s // 10, BLACK)
    circle(x + 14 * s // 10, y - 2, 7 * s // 10, BLACK)
    circle(x - 4, y - 4, 3, WHITE)
    for dy in (-8, 0, 8):
        thick_line((x - 8, y + dy * s // 10),
                   (x - 20 * s // 10, y + dy * s // 10 + 6), 3, BLACK)
        thick_line((x + 8, y + dy * s // 10),
                   (x + 20 * s // 10, y + dy * s // 10 + 6), 3, BLACK)
    thick_line((x + 16, y - 8), (x + 24, y - 16), 2, BLACK)
    thick_line((x + 12, y - 9), (x + 16, y - 18), 2, BLACK)


def flower(x, y, col):
    circle(x, y, 4, col)
    for (dx, dy) in [(-8, 0), (8, 0), (0, -8), (0, 8)]:
        circle(x + dx, y + dy, 5, WHITE)


def render():
    # top band (black) and bottom band (black)
    rect(0, 0, W, 296, BLACK)
    rect(0, 704, W, H, BLACK)

    # middle scene: flat sky, sun with rays, clouds, grass
    rect(0, 296, W, 620, SKY)
    for k in range(8):
        a = k * math.pi / 4.0
        thick_line((150 + 62 * math.cos(a), 372 + 62 * math.sin(a)),
                   (150 + 80 * math.cos(a), 372 + 80 * math.sin(a)), 6, SUN)
    circle(150, 372, 52, SUN)
    for (cx, cy, r) in [(640, 360, 34), (680, 352, 26), (600, 356, 24),
                        (880, 452, 26), (912, 446, 20), (852, 450, 18)]:
        circle(cx, cy, r, WHITE)
    rect(0, 620, W, 704, GRASS)
    rect(0, 620, W, 632, GRASS2)
    flower(90, 668, RED)
    flower(960, 660, PURPLE)
    flower(560, 686, YELLOW)

    # confetti in the sky
    confetti = [(250, 330, RED), (300, 420, YELLOW), (560, 330, PURPLE),
                (620, 430, ORANGE), (760, 340, GREEN), (820, 420, RED),
                (430, 320, YELLOW), (940, 360, PURPLE), (180, 460, GREEN),
                (700, 500, YELLOW)]
    for (cx, cy, col) in confetti:
        rect(cx, cy, cx + 12, cy + 12, col)

    # rocket launching, top right
    poly([(868, 330), (892, 330), (900, 380), (860, 380)], WHITE)
    poly([(868, 330), (880, 300), (892, 330)], RED)
    circle(880, 352, 8, SKY)
    poly([(868, 380), (848, 408), (868, 392)], RED)
    poly([(892, 380), (912, 408), (892, 392)], RED)
    poly([(872, 380), (880, 416), (888, 380)], ORANGE)
    poly([(876, 380), (880, 402), (884, 380)], YELLOW)
    for (sx, sy, sr) in [(852, 428, 12), (880, 440, 14), (908, 428, 11)]:
        circle(sx, sy, sr, WHITE)

    # desk
    rect(240, 596, 784, 628, BROWN)
    rect(240, 596, 784, 604, BROWN_D)
    rect(268, 628, 288, 704, BROWN_D)
    rect(736, 628, 756, 704, BROWN_D)

    # robot, behind the desk on the left
    thick_line((360, 336), (360, 306), 6, DARK)      # antenna
    circle(360, 298, 11, RED)
    rect(296, 336, 424, 452, SILVER)                 # head
    rect(296, 336, 424, 348, SILVER_D)
    rect(296, 336, 308, 452, SILVER_D)
    circle(330, 396, 19, WHITE)                      # eyes
    circle(390, 396, 19, WHITE)
    circle(330, 396, 9, BLACK)
    circle(390, 396, 9, BLACK)
    circle(318, 420, 9, PINK)                        # cheeks
    circle(402, 420, 9, PINK)
    thick_line((344, 428), (360, 438), 5, BLACK)     # smile
    thick_line((360, 438), (376, 428), 5, BLACK)
    rect(284, 452, 436, 600, SILVER)                 # body
    rect(284, 452, 436, 464, SILVER_D)
    rect(308, 488, 412, 560, SCREEN)                 # chest panel
    poly([(340, 500), (380, 500), (380, 516), (340, 516)], GREEN)
    poly([(348, 524), (360, 524), (360, 544), (348, 544)], YELLOW)
    poly([(368, 524), (380, 524), (380, 544), (368, 544)], RED)
    thick_line((284, 500), (252, 560), 12, SILVER)   # arms
    thick_line((436, 500), (468, 560), 12, SILVER)
    circle(250, 564, 9, SILVER_D)
    circle(470, 564, 9, SILVER_D)

    # laptop on the desk, game on its screen
    rect(520, 476, 764, 600, DARK)                   # screen bezel
    rect(536, 492, 748, 584, SKY)                    # game sky
    rect(536, 548, 748, 584, GRASS)                  # game ground
    circle(560, 512, 10, SUN)                        # game sun
    rect(600, 520, 624, 548, RED)                    # pixel hero
    rect(606, 512, 618, 520, RED)
    rect(600, 548, 612, 556, DARK)
    rect(612, 548, 624, 556, DARK)
    circle(660, 528, 8, YELLOW)                      # coins
    circle(700, 520, 8, YELLOW)
    thick_line((726, 548), (726, 500), 4, DARK)      # flag pole
    poly([(726, 500), (726, 514), (748, 507)], GREEN)
    rect(500, 600, 784, 616, SILVER_D)               # laptop base
    rect(500, 600, 784, 606, SILVER)

    # bugs crawling in under the desk
    bug(150, 668, 10)
    bug(880, 672, 10)
    bug(700, 686, 8)

    # the joke: punchline first, huge and legible
    draw_text(["MY AI AGENT", "SHIPPED MY GAME", "IN 4 MINUTES"],
              W // 2, 22, 10, WHITE)
    draw_text(["IT ALSO SHIPPED", "3,000 BUGS",
               "AND A TODO THAT SAYS", "'FIX LATER'"],
              W // 2, 722, 8, WHITE)


# ---------------------------------------------------------------- png
def write_png(path):
    palette = {}
    order = []
    idx = bytearray(W * H)
    for p in range(W * H):
        key = (buf[p * 3], buf[p * 3 + 1], buf[p * 3 + 2])
        j = palette.get(key)
        if j is None:
            j = len(order)
            palette[key] = j
            order.append(key)
        idx[p] = j
    assert len(order) <= 256, len(order)
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += idx[y * W:(y + 1) * W]

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 3, 0, 0, 0))
    png += chunk(b"PLTE", bytes(v for rgb in order for v in rgb))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    render()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    size = write_png(os.path.join(out_dir, "entry.png"))
    print("wrote entry.png:", size, "bytes")


if __name__ == "__main__":
    main()
