"""honu_dev 릴스 엔진 v2 (시안)
모든 것을 180x320칸 도화지에 그리고, 마지막에 한 번만 6배(최근접)로 키운다.
30fps, 120BPM(1박 = 15프레임). 소리는 코드로 합성해 같은 박자표에 올린다.
"""
import math, os, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

LW, LH, SCALE, FPS, BEAT = 180, 320, 6, 30, 15
HERE = os.path.dirname(os.path.abspath(__file__))
FDIR = os.path.join(HERE, "..", "reel", "fonts")
F_R = ImageFont.truetype(os.path.join(FDIR, "Galmuri11.ttf"), 12)
F_B = ImageFont.truetype(os.path.join(FDIR, "Galmuri11-Bold.ttf"), 12)

# ---- 고정 팔레트 ----
INK = (26, 22, 48); BOX = (38, 32, 72); CREAM = (250, 244, 226); GREY = (150, 150, 184)
SKY = [(58, 44, 104), (98, 62, 128), (160, 84, 136), (226, 116, 122), (255, 170, 112), (255, 214, 150)]
SUN = (255, 238, 178); CLOUD = (255, 196, 170); CLOUD_D = (214, 132, 140)
HILL_F = (86, 58, 120); HILL_N = (54, 38, 92)
GRASS_L = (124, 216, 150); GRASS = (70, 170, 130); GRASS_D = (44, 120, 104); SOIL = (58, 40, 72); SOIL_D = (42, 30, 58)
YELLOW = (255, 208, 80); RED = (240, 90, 96); GREEN = (96, 208, 128); PINK = (255, 150, 180)
SL = (124, 196, 255); SL_L = (196, 232, 255); SL_D = (80, 140, 232); WHITE = (255, 255, 255)
WOOD = (168, 110, 98); WOOD_D = (120, 74, 84)
PALETTE = {v for k, v in list(globals().items()) if k.isupper() and isinstance(v, tuple) and len(v) == 3} | set(SKY)

def A(c): return c + (255,)

# ---- 글자 ----
def text_w(s, bold=False):
    return int((F_B if bold else F_R).getlength(s.replace("*", "")))

def draw_text(img, x, y, s, col=CREAM, bold=False, hi=YELLOW, n=None):
    """*별표* 사이는 강조색. n = 보여 줄 글자 수(타자 효과)."""
    d = ImageDraw.Draw(img); d.fontmode = "1"
    f = F_B if bold else F_R
    on = False; shown = 0
    for ch in s:
        if ch == "*": on = not on; continue
        if n is not None and shown >= n: break
        d.text((x, y), ch, font=f, fill=A(hi if on else col))
        x += int(f.getlength(ch)); shown += 1

def nchars(s): return len(s.replace("*", ""))

# ---- 상자 ----
def rrect(d, x, y, w, h, c):
    d.rectangle([x + 1, y, x + w - 2, y + h - 1], fill=A(c)); d.rectangle([x, y + 1, x + w - 1, y + h - 2], fill=A(c))

def panel(img, x, y, w, h, fill=BOX, edge=CREAM, shadow=True):
    d = ImageDraw.Draw(img)
    if shadow: rrect(d, x + 2, y + 2, w, h, INK)
    rrect(d, x, y, w, h, INK); rrect(d, x + 1, y + 1, w - 2, h - 2, edge); rrect(d, x + 2, y + 2, w - 4, h - 4, fill)

def pill(img, cx, y, s, fill=YELLOW, col=INK, bold=True, dy=0):
    w = text_w(s, bold) + 10; x = cx - w // 2
    d = ImageDraw.Draw(img)
    rrect(d, x + 1, y + dy + 2, w, 16, INK); rrect(d, x, y + dy, w, 16, INK); rrect(d, x + 1, y + dy + 1, w - 2, 14, fill)
    draw_text(img, x + 5, y + dy + 2, s, col, bold)

def bubble(img, cx, y, s, tail_x, age, fill=CREAM, col=INK):
    """말풍선. age = 나타난 뒤 지난 프레임(튀어나오는 느낌)."""
    if age < 0: return
    off = [3, -2, -1, 0][age] if age < 4 else 0
    w = text_w(s, True) + 10; x = max(4, min(LW - 4 - w, cx - w // 2)); y += off
    d = ImageDraw.Draw(img)
    rrect(d, x, y, w, 17, INK); rrect(d, x + 1, y + 1, w - 2, 15, fill)
    for k in range(4):
        d.rectangle([tail_x - 3 + k, y + 16 + k, tail_x + 3 - k, y + 16 + k], fill=A(INK))
    for k in range(3):
        d.rectangle([tail_x - 2 + k, y + 15 + k, tail_x + 2 - k, y + 15 + k], fill=A(fill))
    draw_text(img, x + 5, y + 2, s, col, True)

def dialog(img, lines, f, y=60, tick=None):
    """대화창(2줄). f = 창이 뜬 뒤 지난 프레임. 글자는 초당 20자로 찍힌다."""
    panel(img, 9, y, 162, 38)
    n = int(f / 1.5) + 1 if f is not None else 999
    for i, ln in enumerate(lines):
        x = 9 + (162 - text_w(ln, True)) // 2
        draw_text(img, x, y + 6 + i * 14, ln, CREAM, True, n=max(0, n))
        n -= nchars(ln)
    if f is not None and n >= 0 and f >= 0:      # 다 찍히면 깜빡이는 ▼
        d = ImageDraw.Draw(img); by = y + 30 + (f // 8) % 2
        for k in range(3): d.rectangle([158 + k, by + k, 164 - k, by + k], fill=A(YELLOW))

# ---- 스프라이트 ----
def sprite(rows, pal):
    im = Image.new("RGBA", (len(rows[0]), len(rows)), (0, 0, 0, 0))
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c in pal: im.putpixel((x, y), A(pal[c]))
    return im

_sl = {}
SW, SH = 46, 35              # 슬라임 기본 크기(칸)
def slime(w=SW, h=SH, face="base", look=0):
    k = (w, h, face, look)
    if k in _sl: return _sl[k]
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ins = set()
    for j in range(h):
        u = (h - j - 0.5) / h
        x = w / 2 * (1 - u ** 2.6) ** (1 / 2.6)
        if j == h - 1: x -= 3
        elif j == h - 2: x -= 1
        hw = max(4, int(round(x)))
        for i in range(w // 2 - hw, w // 2 + hw): ins.add((i, j))
    def edge(p, r=1):
        i, j = p
        return any((i + a, j + b) not in ins for a, b in ((r, 0), (-r, 0), (0, r), (0, -r)))
    for p in ins:
        i, j = p
        if edge(p): c = INK
        elif j >= h - 5 or (i + 4, j) not in ins: c = SL_D
        elif ((i - 3, j) not in ins and j < h * 0.62) or ((i, j - 3) not in ins and i < w * 0.6): c = SL_L
        else: c = SL
        im.putpixel(p, A(c))
    sx, sy = int(w * 0.24), int(h * 0.2)
    for a, b in ((0, 0), (1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1), (0, 2), (6, 0), (6, 1)):
        q = (sx + a, sy + b)
        if q in ins and not edge(q): im.putpixel(q, A(WHITE))
    ey = int(h * 0.43); eh = 8 if h >= 33 else 7
    def px(x, y, c=INK):
        if 0 <= x < w and 0 <= y < h: im.putpixel((x, y), A(c))
    for s in (-1, 1):
        ex = w // 2 + (-10 if s < 0 else 7) + look
        if face == "blink":
            for a in range(4):
                for b in (4, 5): px(ex + a - (1 if s > 0 else 0), ey + b)
        elif face == "happy":
            for a, b in ((0, 4), (0, 3), (1, 2), (1, 1), (2, 0), (3, 0), (4, 1), (4, 2), (5, 3), (5, 4), (1, 3), (4, 3), (2, 1), (3, 1)):
                px(ex - 1 + a, ey + 1 + b)
        elif face == "sad":
            for a in range(3):
                for b in range(3, eh): px(ex + a, ey + b)
            for a in range(6):
                yy = ey + (a // 2 if s > 0 else 2 - a // 2)
                px(ex - 1 + a - (1 if s > 0 else 0), yy)
        else:
            for a in range(3):
                for b in range(eh): px(ex + a, ey + b)
            px(ex, ey, WHITE); px(ex + 1, ey, WHITE) if face == "wow" else None
            if face == "wow":
                for a in range(3): px(ex + a, ey - 1)
        cx = ex + (-6 if s < 0 else 6)
        for a in range(3):
            for b in range(2):
                q = (cx + a, ey + eh + b)
                if q in ins and not edge(q, 2): px(q[0], q[1], PINK)
    mx = w // 2 - 2 + look; my = ey + eh + 1
    if face == "wow":
        for a in range(4):
            for b in range(4): px(mx + a, my - 1 + b)
        px(mx + 1, my, RED); px(mx + 2, my, RED); px(mx + 1, my + 1, RED); px(mx + 2, my + 1, RED)
    elif face == "happy":
        for a, b in ((-1, 0), (-1, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 1), (4, 0)): px(mx + a, my + b)
    elif face == "sad":
        for a, b in ((-1, 2), (0, 1), (1, 0), (2, 0), (3, 1), (4, 2)): px(mx + a, my + 1 + b)
    else:
        for a in range(4): px(mx + a, my + 1)
    _sl[k] = im
    return im

def hop(p, height=18):
    """p: 0~1 한 번 뛰기. (올라간 높이, 너비, 높이). 뛰기 전 눌림, 오를 때 늘어남, 착지 때 더 눌림."""
    if p < 0 or p >= 1: return 0, SW, SH
    if p < 0.14: return 0, 52, 31
    if p > 0.86: return 0, 54, 30
    q = (p - 0.14) / 0.72
    yy = int(round(height * 4 * q * (1 - q)))
    if q < 0.3 or q > 0.75: return yy, 40, 40
    return yy, SW, SH

def put_slime(img, cx, ground, f, face="base", look=0, jump=None, idle=True):
    yy, w, h = jump if jump else (0, SW, SH)
    if not jump and idle and (f // 14) % 2: w, h = 48, 34
    if face == "base" and f % 76 in (0, 1, 2): face = "blink"
    s = slime(w, h, face, look)
    img.alpha_composite(s, (cx - w // 2, ground - h - yy))

_BOT = [
    "..........yy..........", ".........yyyy.........", "..........ii..........", "..........ii..........",
    "...iiiiiiiiiiiiiiii...", "..iwwwwwwwwwwwwwwwwi..", "..iwwwwwwwwwwwwwwwwi..", "..iwwiiiiiiiiiiiiwwi..",
    "..iwwiiggiiiiggiiwwi..", "..iwwiiggiiiiggiiwwi..", "..iwwiiggiiiiggiiwwi..", "..iwwiiiiiiiiiiiiwwi..",
    "..iwwwwwwwwwwwwwwwwi..", "..iddddddddddddddddi..", "...iiiiiiiiiiiiiiii...", ".....iaaaaaaaaaai.....",
    "..iiiiaaayyyyaaaiiii..", "..iaaiaaayyyyaaaiaai..", "..iiiiaaaaaaaaaaiiii..", ".....iddddddddddi.....",
    "......iiii..iiii......", ".....iiiii..iiiii....."]
BOT = sprite(_BOT, {"y": YELLOW, "i": INK, "w": CREAM, "g": GREEN, "a": GREY, "d": (112, 112, 150)})
BOT_ON = sprite(_BOT, {"y": YELLOW, "i": INK, "w": CREAM, "g": YELLOW, "a": GREY, "d": (112, 112, 150)})
BW, BH = 22, 22
HEART = sprite([".rr...rr.", "rrrr.rrrr", "rwrrrrrrr", "rrrrrrrrr", ".rrrrrrr.", "..rrrrr..", "...rrr...", "....r...."], {"r": RED, "w": CREAM})
CHECK = sprite([".....ii", "....iii", "ii.iii.", "iiiii..", ".iii...", "..i...."], {"i": INK})
STAR_B = sprite(["..w..", "..w..", "wwwww", "..w..", "..w.."], {"w": CREAM})
STAR_S = sprite([".w.", "www", ".w."], {"w": CREAM})
STAR_Y = sprite(["..w..", "..w..", "wwwww", "..w..", "..w.."], {"w": YELLOW})
PINE = sprite(["...p...", "..ppp..", "..ppp..", ".ppppp.", ".ppppp.", "ppppppp", "ppppppp", "...p...", "...p..."], {"p": HILL_N})
CL1 = sprite(["......cccccc........", "...ccccccccccc..ccc.", ".cccccccccccccccccc.", "cccccccccccccccccccc", ".dddddddddddddddddd."], {"c": CLOUD, "d": CLOUD_D})
CL2 = sprite(["...cccc.....", ".ccccccccc..", "cccccccccccc", ".dddddddddd."], {"c": CLOUD, "d": CLOUD_D})

def put(img, sp, x, y): img.alpha_composite(sp, (int(x), int(y)))

def put_bot(img, cx, ground, f, on=False, jump=0):
    put(img, BOT_ON if on else BOT, cx - BW // 2, ground - BH - jump - ((f // 10) % 2 if not jump else 0))

def phone(img, cx, cy):
    d = ImageDraw.Draw(img)
    rrect(d, cx - 11, cy - 17, 22, 34, INK); rrect(d, cx - 10, cy - 16, 20, 32, CREAM)
    d.rectangle([cx - 8, cy - 12, cx + 7, cy + 10], fill=A(BOX))
    rrect(d, cx - 5, cy - 9, 10, 10, YELLOW); d.rectangle([cx - 5, cy + 4, cx + 4, cy + 5], fill=A(GREEN)); d.rectangle([cx - 5, cy + 7, cx + 1, cy + 8], fill=A(GREY))
    d.rectangle([cx - 2, cy + 12, cx + 1, cy + 13], fill=A(INK))

MON_W = 56
def monitor(img, x, ground, screen):
    """책상 위 모니터(화면 50x32칸). screen(d, sx, sy) 가 화면 안을 그린다."""
    d = ImageDraw.Draw(img)
    d.rectangle([x - 5, ground - 16, x + 60, ground - 12], fill=A(INK)); d.rectangle([x - 4, ground - 15, x + 59, ground - 13], fill=A(WOOD))
    for lx in (x, x + 51):
        d.rectangle([lx, ground - 11, lx + 4, ground - 1], fill=A(INK)); d.rectangle([lx + 1, ground - 11, lx + 3, ground - 1], fill=A(WOOD_D))
    d.rectangle([x + 23, ground - 21, x + 32, ground - 17], fill=A(INK))
    rrect(d, x, ground - 60, 56, 40, INK); rrect(d, x + 1, ground - 59, 54, 38, GREY)
    d.rectangle([x + 3, ground - 57, x + 52, ground - 26], fill=A(BOX))
    d.rectangle([x + 26, ground - 24, x + 29, ground - 23], fill=A(GREEN))
    screen(d, x + 3, ground - 57)

# ---- 배경 (겹겹이, 정수 칸 단위 이동) ----
random.seed(7)
STARS = [(random.randrange(4, LW - 4), random.randrange(4, 120), random.randrange(4)) for _ in range(26)]
def _hills(col, base, amp, per, ph, trees=False):
    im = Image.new("RGBA", (360, LH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for x in range(360):
        h = base + int(round(amp * math.sin(2 * math.pi * x / per + ph) + amp * 0.5 * math.sin(4 * math.pi * x / per + ph * 2)))
        d.line([x, 232 - h, x, 232], fill=A(col))
        if trees and x % 45 == 20: im.alpha_composite(PINE, (x - 3, 232 - h - 8))
    return im
L_FAR = _hills(HILL_F, 34, 9, 180, 1.0); L_NEAR = _hills(HILL_N, 16, 6, 120, 2.0, True)
def _ground():
    im = Image.new("RGBA", (360, LH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 232, 359, 232], fill=A(GRASS_L)); d.rectangle([0, 233, 359, 236], fill=A(GRASS)); d.rectangle([0, 237, 359, 238], fill=A(GRASS_D))
    d.rectangle([0, 239, 359, LH], fill=A(SOIL))
    r = random.Random(3)
    for x in range(0, 360, 6):
        if r.random() < 0.5: d.rectangle([x, 230, x + 1, 231], fill=A(GRASS_L))
        d.rectangle([x + 2, 239, x + 4, 239 + r.randrange(1, 4)], fill=A(GRASS_D))
    for _ in range(90):
        x, y = r.randrange(0, 356), r.randrange(246, LH - 4)
        d.rectangle([x, y, x + 3, y + 1], fill=A(SOIL_D))
    for gx, gy, c in ((40, 262, YELLOW), (150, 286, GREEN), (250, 270, RED), (320, 296, SL)):   # 땅속 보석
        for a, b in ((1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (3, 1), (1, 2), (2, 2)): d.point((gx + a, gy + b), fill=A(c))
        d.point((gx + 1, gy + 1), fill=A(CREAM))
    return im
L_GROUND = _ground()
def _sky():
    im = Image.new("RGBA", (LW, LH), A(SKY[0])); d = ImageDraw.Draw(im)
    ys = [0, 78, 128, 166, 194, 214, 233]
    for i in range(6):
        d.rectangle([0, ys[i], LW, ys[i + 1]], fill=A(SKY[i]))
        if i: 
            for x in range(0, LW, 16): d.rectangle([x, ys[i] - 2, x + 7, ys[i] - 1], fill=A(SKY[i]))
    return im
L_SKY = _sky()
def _tile(img, layer, off):
    off = int(off) % 360
    img.alpha_composite(layer, (-off, 0)); img.alpha_composite(layer, (360 - off, 0))

def background(f, cam):
    img = L_SKY.copy(); d = ImageDraw.Draw(img)
    for x, y, ph in STARS:
        st = (f // 12 + ph) % 4
        if st == 0: put(img, STAR_S, x - 1, y - 1)
        elif st != 2: d.point((x, y), fill=A(CREAM))
    sx = 128 - int(cam * 0.04) % 400
    d.ellipse([sx - 24, 186, sx + 24, 234], fill=A(SUN))
    for i, (cl, x0, y) in enumerate(((CL1, 20, 96), (CL2, 120, 140), (CL1, 190, 170), (CL2, 250, 110))):
        x = (x0 - int(cam * 0.15) - f // (3 + 2 * (i % 2))) % 300 - 40
        put(img, cl, x, y)
    _tile(img, L_FAR, cam * 0.3); _tile(img, L_NEAR, cam * 0.55); _tile(img, L_GROUND, cam)
    return img

def dust(img, x, ground, age):
    if 0 <= age < 9:
        d = ImageDraw.Draw(img); s = 3 if age < 4 else (2 if age < 7 else 1)
        for sgn in (-1, 1):
            for k in (0, 1):
                px = x + sgn * (20 + age * 2 + k * 6); py = ground - 3 - age // 2 - k * 4
                d.rectangle([px, py, px + s, py + s], fill=A(CREAM))

def sparkle(img, cx, cy, f, r=14, sp=STAR_B):
    for k in range(4):
        a = f * 0.12 + k * math.pi / 2
        x, y = cx + int(round(r * math.cos(a))), cy + int(round(r * 0.8 * math.sin(a)))
        put(img, sp if (f // 6 + k) % 2 else STAR_S, x - (2 if (f // 6 + k) % 2 else 1), y - (2 if (f // 6 + k) % 2 else 1))

def blinds(img, k):
    """세로 블라인드 전환. k = 0(열림)~6(닫힘)."""
    if k <= 0: return
    d = ImageDraw.Draw(img)
    for x in range(0, LW, 12): d.rectangle([x, 0, x + k * 2 - 1, LH], fill=A(INK))

# ---- 소리 (코드로 합성) ----
SR = 48000
def _env(n, a=0.005, r=0.05):
    e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr); return e
def tone(freq, dur, kind="sq", duty=0.5, vol=0.3, f2=None, r=0.05):
    n = int(dur * SR); t = np.arange(n) / SR
    fr = np.linspace(freq, f2, n) if f2 else np.full(n, float(freq))
    ph = np.cumsum(fr) / SR
    if kind == "sq": w = np.where((ph % 1) < duty, 1.0, -1.0)
    elif kind == "tri": w = 2 * np.abs(2 * (ph % 1) - 1) - 1
    else:
        rs = np.random.RandomState(1); step = max(1, int(SR / max(freq, 1)))
        w = np.repeat(rs.uniform(-1, 1, n // step + 1), step)[:n]
    return w * _env(n, r=min(r, dur / 2)) * vol
N = lambda s: 440 * 2 ** ((s - 9) / 12)   # s = C4 기준 반음 수
def sfx(name, k=0):
    if name == "tick": return tone(1500, 0.018, vol=0.10, r=0.01)
    if name == "jump": return tone(330, 0.12, duty=0.25, vol=0.20, f2=760)
    if name == "land": return np.concatenate([tone(90, 0.07, "noise", vol=0.30), tone(110, 0.08, "tri", vol=0.4, f2=60)])
    if name == "pop": return tone(N(12 + 2 * k), 0.07, duty=0.25, vol=0.22, f2=N(19 + 2 * k))
    if name == "check": return np.concatenate([tone(N(16), 0.07, vol=0.22), tone(N(23), 0.16, vol=0.22, r=0.1)])
    if name == "error": return np.concatenate([tone(140, 0.12, vol=0.22), np.zeros(int(0.04 * SR)), tone(105, 0.2, vol=0.22)])
    if name == "shutter": return np.concatenate([tone(4000, 0.03, "noise", vol=0.35), np.zeros(int(0.05 * SR)), tone(2500, 0.05, "noise", vol=0.3)])
    if name == "whoosh": return tone(300, 0.22, "noise", vol=0.16, f2=3000, r=0.1)
    if name == "fanfare": return np.concatenate([tone(N(s), d, duty=0.25, vol=0.26, r=0.04) for s, d in ((12, .1), (16, .1), (19, .1), (24, .32))])
    if name == "drop": return tone(900, 0.22, duty=0.25, vol=0.16, f2=260)
    raise KeyError(name)

def music(beats, plan):
    """plan: 박마다 (코드 근음 반음, 단조 여부, 세기). 베이스 + 아르페지오 + 하이햇."""
    out = np.zeros(int(beats * 0.5 * SR) + SR)
    for b in range(int(beats)):
        root, minor, lvl = plan(b)
        if lvl <= 0: continue
        t0 = int(b * 0.5 * SR)
        third = 3 if minor else 4
        bass = tone(N(root - 24), 0.22, "tri", vol=0.30 * lvl)
        out[t0:t0 + len(bass)] += bass
        for i, st in enumerate((0, third, 7, 12) if b % 2 == 0 else (7, third, 12, 7)):
            if lvl < 0.6 and i % 2: continue
            a = tone(N(root + st), 0.11, duty=0.125, vol=0.075 * lvl, r=0.06)
            p = t0 + int(i * 0.125 * SR); out[p:p + len(a)] += a
        h = tone(8000, 0.03, "noise", vol=0.05 * lvl, r=0.02)
        p = t0 + int(0.25 * SR); out[p:p + len(h)] += h
    return out

def mix(total_frames, events, bgm=None):
    out = np.zeros(int(total_frames / FPS * SR) + SR)
    if bgm is not None: out[:len(bgm)] += bgm[:len(out)]
    for fr, name, k in events:
        s = sfx(name, k); p = int(fr / FPS * SR)
        if p + len(s) < len(out): out[p:p + len(s)] += s
    out = out[:int(total_frames / FPS * SR)]
    return np.clip(out, -1, 1)

def write_wav(path, x):
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767 * 0.8).astype("<i2").tobytes())

def render(frame_fn, total, out_mp4, wav=None, lufs=-14):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{LW}x{LH}", "-r", str(FPS), "-i", "-"]
    if wav: cmd += ["-i", wav]
    cmd += ["-vf", f"scale={LW*SCALE}:{LH*SCALE}:flags=neighbor,format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "12",
            "-g", "30", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-movflags", "+faststart"]
    if wav: cmd += ["-af", f"loudnorm=I={lufs}:TP=-2:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest"]
    p = subprocess.Popen(cmd + [out_mp4], stdin=subprocess.PIPE)
    for f in range(total): p.stdin.write(frame_fn(f).convert("RGB").tobytes())
    p.stdin.close(); p.wait()
