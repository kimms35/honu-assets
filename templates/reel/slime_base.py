import math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
OUT = os.path.dirname(os.path.abspath(__file__))
# 글꼴: 갈무리11 (픽셀 글꼴, SIL OFL 1.1 — fonts/OFL-Galmuri.md)
FONT_B = os.path.join(OUT, "fonts", "Galmuri11-Bold.ttf")
FONT_M = os.path.join(OUT, "fonts", "Galmuri11-Bold.ttf")
FONT_R = os.path.join(OUT, "fonts", "Galmuri11.ttf")
KR = 1
_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size, index=KR if path.endswith(".ttc") else 0)
    return _fc[k]

INK = (34, 32, 64)
SKY = (226, 236, 255)
YELLOW = (255, 206, 84)
CORAL = (255, 104, 104)
GREENC = (64, 196, 120)
SOFT = (110, 112, 150)
WHITE = (255, 255, 255)
# slime colours (original character)
S_OUT = (38, 36, 84)
S_BASE = (120, 150, 255)
S_SHADE = (88, 108, 222)
S_LIGHT = (176, 196, 255)
S_PINK = (255, 150, 190)

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))
def ease_out(x):
    x = clamp(x); return 1 - (1 - x) ** 3
def ease_back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def appear(t, start, dur=0.4):
    return ease_out((t - start) / dur)

# ---------- background: flat sky + drifting pixel clouds ----------
PX = 12
def cloud_img(cols):
    pattern = ["..XXXX......", ".XXXXXXX.XX.", "XXXXXXXXXXXX", "XXXXXXXXXXXX", ".SSSSSSSSSS."]
    pattern = [r[:cols] for r in pattern]
    im = Image.new("RGBA", (len(pattern[0]), len(pattern)), (0, 0, 0, 0))
    for y, r in enumerate(pattern):
        for x, c in enumerate(r):
            if c == "X": im.putpixel((x, y), (255, 255, 255, 230))
            elif c == "S": im.putpixel((x, y), (200, 214, 245, 230))
    return im.resize((im.width * PX, im.height * PX), Image.NEAREST)
CLOUD = cloud_img(12)
random.seed(5)
CLOUDS = [(random.uniform(-200, W), random.uniform(80, H - 200), random.uniform(18, 40), random.choice([1.0, 1.5])) for _ in range(7)]
SPARK = [(random.randrange(0, W // PX) * PX, random.randrange(0, H // PX) * PX, random.uniform(0, 6.28)) for _ in range(40)]

def draw_bg(img, gt):
    d = ImageDraw.Draw(img)
    for x, y, ph in SPARK:
        if math.sin(gt * 3 + ph) > 0.6:
            d.rectangle([x, y, x + PX - 1, y + PX - 1], fill=(255, 255, 255, 255))
    for x0, y, sp, s in CLOUDS:
        x = (x0 + gt * sp) % (W + 300) - 300
        c = CLOUD if s == 1.0 else CLOUD.resize((int(CLOUD.width * 1.5), int(CLOUD.height * 1.5)), Image.NEAREST)
        img.alpha_composite(c, (int(x // PX * PX), int(y // PX * PX)))

# ---------- pixel slime ----------
def slime_sprite(sx, sy, mood="happy", blink=False):
    """Draw a round slime on a small pixel grid; returns RGBA sprite at grid resolution."""
    G = 30
    im = Image.new("RGBA", (G, G), (0, 0, 0, 0))
    rx, ry = 11.5 * sx, 10.5 * sy
    cx, base = G / 2, G - 2  # bottom of the slime sits on base row
    cy = base - ry * 0.9
    inside = set()
    for j in range(G):
        for i in range(G):
            x = (i + 0.5 - cx) / rx
            y = (j + 0.5 - cy) / ry
            if x * x + y * y <= 1.0 and (j + 0.5) <= base:
                inside.add((i, j))
    for (i, j) in inside:
        nb = [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]
        if any(n not in inside for n in nb):
            c = S_OUT
        else:
            y = (j + 0.5 - cy) / ry
            c = S_SHADE if y > 0.45 else S_BASE
        im.putpixel((i, j), c + (255,))
    # highlight
    hx, hy = int(cx - rx * 0.5), int(cy - ry * 0.55)
    for (a, b, c) in [(0, 0, WHITE), (1, 0, S_LIGHT), (0, 1, S_LIGHT), (2, 1, S_LIGHT), (1, 1, S_LIGHT)]:
        if (hx + a, hy + b) in inside:
            im.putpixel((hx + a, hy + b), c + (255,))
    # face
    fy = int(round(cy + ry * 0.05))
    for s in (-1, 1):
        ex = int(round(cx + s * rx * 0.36)) - (1 if s < 0 else 0)
        if blink:
            im.putpixel((ex, fy + 1), S_OUT + (255,)); im.putpixel((ex + 1, fy + 1), S_OUT + (255,))
        else:
            for dx in (0, 1):
                for dy in (0, 1, 2):
                    im.putpixel((ex + dx, fy + dy), S_OUT + (255,))
            im.putpixel((ex + (1 if s < 0 else 0), fy), WHITE + (255,))
        bx = int(round(cx + s * rx * 0.62)) - (1 if s < 0 else 0)
        for dx in (0, 1):
            if (bx + dx, fy + 3) in inside:
                im.putpixel((bx + dx, fy + 3), S_PINK + (255,))
    my = fy + 3
    if mood == "happy":
        for px in [(-1, 0), (0, 1), (1, 1), (2, 0)]:
            im.putpixel((int(cx) - 1 + px[0], my + px[1]), S_OUT + (255,))
    else:  # "o" mouth
        for px in [(0, 0), (1, 0), (0, 1), (1, 1)]:
            im.putpixel((int(cx) - 1 + px[0], my + px[1]), S_OUT + (255,))
    return im

def draw_slime(base, cx, ground, scale, t, hop=1.0, mood="happy", period=0.9):
    ph = (t / period) % 1.0
    air = math.sin(math.pi * ph)
    jump = air * 150 * scale * hop
    land = max(0.0, 1 - ph / 0.14) + max(0.0, (ph - 0.86) / 0.14)
    sq = land * 0.22 * hop
    st = air * 0.08 * hop
    sx, sy = 1 + sq - st, 1 - sq + st
    blink = (t % 3.0) > 2.85
    spr = slime_sprite(sx, sy, mood, blink)
    P = int(16 * scale)
    big = spr.resize((spr.width * P, spr.height * P), Image.NEAREST)
    # shadow
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sw = int((150 - air * 50 * hop) * scale)
    ImageDraw.Draw(sh).rectangle([cx - sw, ground - 6 * scale, cx + sw, ground + 10 * scale], fill=(34, 32, 64, 40))
    base.alpha_composite(sh)
    base.alpha_composite(big, (int(cx - big.width / 2), int(ground - big.height + 2 * P - jump)))

# ---------- blocky UI ----------
def text_c(d, y, s, f, color, a=1.0, x=None, shadow=False):
    if a <= 0:
        return
    bb = d.textbbox((0, 0), s, font=f)
    w = bb[2] - bb[0]
    xx = (W - w) / 2 if x is None else x
    al = int(255 * clamp(a))
    if shadow:
        d.text((xx + 6, y + 6), s, font=f, fill=(34, 32, 64, int(al * 0.25)))
    d.text((xx, y), s, font=f, fill=color + (al,))

def block(d, box, fill, a, off=10):
    al = int(255 * clamp(a))
    x0, y0, x1, y1 = box
    d.rectangle([x0 + off, y0 + off, x1 + off, y1 + off], fill=INK + (al,))
    d.rectangle(box, fill=fill + (al,), outline=INK + (al,), width=6)

# ---------- scenes ----------
def scene_hook(img, d, t, T):
    a1 = appear(t, 0.2); a2 = appear(t, 0.8)
    block(d, [320, 300 - (1 - a1) * 40, 760, 400 - (1 - a1) * 40], YELLOW, a1, 8)
    text_c(d, 312 - (1 - a1) * 40, "코딩 0일차", font(FONT_B, 62), INK, a1)
    text_c(d, 470 + (1 - a2) * 50, "클로드로", font(FONT_B, 120), INK, a2, shadow=True)
    text_c(d, 620 + (1 - a2) * 50, "SNS 자동화", font(FONT_B, 120), CORAL, a2, shadow=True)
    text_c(d, 770 + (1 - a2) * 50, "시작했어요", font(FONT_B, 120), INK, a2, shadow=True)
    if t > 0.3:
        drop = ease_out((t - 0.3) / 0.5)
        draw_slime(img, W / 2, 1560 - (1 - drop) * 900, 1.2, t, hop=1.0 if drop >= 1 else 0)

def scene_zero(img, d, t, T):
    a1 = appear(t, 0.1); a2 = appear(t, 0.8); a3 = appear(t, 1.8)
    text_c(d, 330, "개발 지식", font(FONT_M, 76), SOFT, a1)
    s = ease_back((t - 0.4) / 0.5) if t > 0.4 else 0
    if s > 0:
        text_c(d, 430 + (1 - s) * 120, "0", font(FONT_B, int(300 * max(0.01, s))), CORAL, 1, shadow=True)
    text_c(d, 830, "코드는 한 줄도", font(FONT_B, 92), INK, a2)
    text_c(d, 950, "안 썼어요", font(FONT_B, 92), INK, a2)
    text_c(d, 1100, "말로만 시켰어요", font(FONT_M, 64), S_SHADE, a3)
    draw_slime(img, W / 2, 1640, 0.9, t, hop=0.35, mood="o", period=1.4)
    if t > 1.2:
        q = ease_back((t - 1.2) / 0.4)
        text_c(d, 1250 - q * 20, "?", font(FONT_B, int(110 * max(q, .01))), CORAL, 1, x=W / 2 + 170)

ITEMS = [("인스타 크리에이터 계정 전환", "1"), ("Buffer로 예약 발행 연결", "2"), ("Notion 콘텐츠 보드 만들기", "3")]

def scene_list(img, d, t, T):
    a = appear(t, 0.1)
    text_c(d, 280 - (1 - a) * 30, "오늘 한 일", font(FONT_B, 110), INK, a, shadow=True)
    text_c(d, 430, "딱 3개", font(FONT_M, 64), S_SHADE, appear(t, 0.5))
    for i, (s, n) in enumerate(ITEMS):
        st = 1.0 + i * 1.6
        ai = appear(t, st, 0.4)
        y = 620 + i * 250
        x0 = 80 + (1 - ai) * -120
        block(d, [x0, y, x0 + 910, y + 180], WHITE, ai)
        al = int(255 * ai)
        d.rectangle([x0 + 36, y + 45, x0 + 126, y + 135], fill=YELLOW + (al,), outline=INK + (al,), width=5)
        bb = d.textbbox((0, 0), n, font=font(FONT_B, 54))
        d.text((x0 + 81 - (bb[2] - bb[0]) / 2, y + 52), n, font=font(FONT_B, 54), fill=INK + (al,))
        d.text((x0 + 156, y + 60), s, font=font(FONT_M, 48), fill=INK + (al,))
        ck = clamp((t - st - 0.7) / 0.3)
        if ck > 0:
            # pixel checkmark, revealed block by block
            cells = [(0, 2), (1, 3), (2, 4), (3, 3), (4, 2), (5, 1), (6, 0)]
            cx0, cy0 = x0 + 790, y + 50
            for c, (gx, gy) in enumerate(cells):
                if c / len(cells) <= ck:
                    d.rectangle([cx0 + gx * 14, cy0 + gy * 14, cx0 + gx * 14 + 17, cy0 + gy * 14 + 17], fill=GREENC + (255,))
    # slime hops once per item as it gets checked
    hop = 0.0
    for i in range(3):
        st = 1.0 + i * 1.6 + 0.7
        if st <= t <= st + 0.9:
            hop = 1.0
    draw_slime(img, 860, 1700, 0.6, t, hop=max(hop, 0.25), period=0.9)

STAGES = ["수집", "선별", "생성", "예약", "분석"]

def scene_flow(img, d, t, T):
    a = appear(t, 0.1)
    text_c(d, 260, "그래서 이렇게", font(FONT_M, 70), SOFT, a)
    text_c(d, 360, "돌아가요", font(FONT_B, 110), INK, a, shadow=True)
    ys = [600 + i * 190 for i in range(5)]
    k = int((t - 2.4) * 2.2) % 5 if t > 2.4 else -1
    for i, s in enumerate(STAGES):
        ai = appear(t, 0.5 + i * 0.35, 0.35)
        y = ys[i]
        block(d, [300, y, 780, y + 120], YELLOW if i == k else WHITE, ai, 8)
        text_c(d, y + 22, s, font(FONT_B, 60), INK, ai)
        if i < 4:
            la = appear(t, 0.7 + i * 0.35, 0.3)
            d.rectangle([534, y + 128, 546, y + 128 + 62 * la], fill=INK + (int(255 * la),))
    la = appear(t, 2.3, 0.5)
    if la > 0:
        c = CORAL + (int(255 * la),)
        d.rectangle([800, ys[4] + 54, 900, ys[4] + 66], fill=c)
        d.rectangle([888, ys[0] + 54, 900, ys[4] + 66], fill=c)
        d.rectangle([816, ys[0] + 54, 900, ys[0] + 66], fill=c)
        d.polygon([(816, ys[0] + 36), (816, ys[0] + 84), (796, ys[0] + 60)], fill=c)
    # slime rides the active stage
    if k >= 0:
        draw_slime(img, 210, ys[k] + 118, 0.45, t, hop=0.6, period=0.45)
    text_c(d, 1620, "이 영상도 클로드가 만들었어요", font(FONT_M, 54), CORAL, appear(t, 3.4))

def scene_cta(img, d, t, T):
    a1 = appear(t, 0.2); a2 = appear(t, 0.8); a3 = appear(t, 1.4)
    draw_slime(img, W / 2, 860, 1.05, t, hop=1.0, period=0.7)
    text_c(d, 960, "왕초보의", font(FONT_M, 76), SOFT, a1)
    text_c(d, 1070, "앱 개발기", font(FONT_B, 130), INK, a1, shadow=True)
    text_c(d, 1240, "같이 봐요", font(FONT_B, 130), CORAL, a2, shadow=True)
    block(d, [300, 1480, 780, 1590], YELLOW, a3, 8)
    text_c(d, 1495, "@honu_dev", font(FONT_B, 66), INK, a3)
    text_c(d, 1650, "팔로우하고 다음 편에서 만나요", font(FONT_R, 46), INK, appear(t, 2.0))

SCENES = [("s1", scene_hook, 4.2), ("s2", scene_zero, 4.6), ("s3", scene_list, 6.6), ("s4", scene_flow, 6.0), ("s5", scene_cta, 5.0)]

def frame(fn, t, T, gt):
    img = Image.new("RGBA", (W, H), SKY + (255,))
    draw_bg(img, gt)
    bg_only = img.copy()
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fn(img, ImageDraw.Draw(ov), t, T)
    img.alpha_composite(ov)
    fade = min(clamp(t / 0.2), clamp((T - t) / 0.2))
    if fade < 1:
        img = Image.blend(bg_only, img, fade)
    hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(hl).text((60, 130), "honu_dev", font=font(FONT_M, 40), fill=INK + (140,)); img.alpha_composite(hl)
    return img.convert("RGB")

def render(stills=None):
    gt0 = 0.0
    for name, fn, T in SCENES:
        if stills is not None:
            for st in stills.get(name, []):
                frame(fn, st, T, gt0 + st).save(os.path.join(OUT, f"v4_still_{name}_{st}.jpg"), quality=88)
            gt0 += T; continue
        n = int(round(T * FPS))
        tmp = os.path.join(OUT, f"v4_{name}.tmp.mp4")
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
        for i in range(n):
            t = i / FPS
            p.stdin.write(frame(fn, t, T, gt0 + t).tobytes())
        p.stdin.close()
        if p.wait() == 0:
            os.replace(tmp, os.path.join(OUT, f"v4_{name}.mp4"))
        gt0 += T

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        render(stills={"s1": [3.0, 3.45], "s2": [3.0], "s3": [6.0], "s4": [4.0], "s5": [3.0]})
    else:
        render()
