import os, subprocess, sys
from PIL import Image, ImageDraw
from slime_base import (W, H, FPS, OUT, FONT_B, FONT_M, FONT_R, INK, YELLOW, CORAL, GREENC, SOFT, WHITE, S_SHADE,
                        font, text_c, block, draw_slime, draw_bg, appear, ease_back, ease_out, clamp, SKY)


import math
# ---------- original mascot: chunky pixel slime with a sprout ----------
C_OUT = (40, 44, 72)
C_BODY = (158, 232, 178)
C_SHADE = (112, 204, 150)
C_LEAF = (52, 168, 104)
C_PINK = (255, 150, 170)

C_BODY2 = (150, 208, 255)
ROWS = [
    ".....OOOOOO.....",
    "...OOBBBBBBOO...",
    "..OBWWBBBBBBBO..",
    ".OBWBBBBBBBBBBO.",
    ".OBBBBBBBBBBBBO.",
    "OBBBBBBBBBBBBBBO",
    "OBBBEEBBBBEEBBBO",
    "OBBBEEBBBBEEBBBO",
    "OBBBEEBBBBEEBBBO",
    "OBBBEEBBBBEEBBBO",
    "OBBBBBBBBBBBBBBO",
    "OBBBBBBBBBBBBBBO",
    ".OBBBBBBBBBBBBO.",
    "..OOOOOOOOOOOO..",
]
assert all(len(r) == 16 for r in ROWS)
PAL = {"O": C_OUT, "M": C_OUT, "B": C_BODY2, "W": WHITE, "E": (24, 24, 40)}

def slime_sprite(mood="happy", blink=False):
    rows = list(ROWS)
    if blink:
        for j in (6, 7, 9):
            rows[j] = "OBBBBBBBBBBBBBBO"
    if mood != "happy":
        rows[11] = "OBBBBBBMMBBBBBBO"
    im = Image.new("RGBA", (16, len(rows)), (0, 0, 0, 0))
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != ".":
                im.putpixel((i, j), PAL[ch] + (255,))
    return im

def draw_slime(base, cx, ground, scale, t, hop=1.0, mood="happy", period=0.9):
    ph = (t / period) % 1.0
    air = math.sin(math.pi * ph)
    jump = air * 150 * scale * hop
    land = max(0.0, 1 - ph / 0.14) + max(0.0, (ph - 0.86) / 0.14)
    sq = land * 0.2 * hop; st = air * 0.07 * hop
    spr = slime_sprite(mood, (t % 3.0) > 2.85)
    P = 30 * scale
    big = spr.resize((int(16 * P * (1 + sq - st)), int(14 * P * (1 - sq + st))), Image.NEAREST)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sw = int((190 - air * 60 * hop) * scale)
    ImageDraw.Draw(sh).rectangle([cx - sw, ground - 4 * scale, cx + sw, ground + 12 * scale], fill=(34, 32, 64, 40))
    base.alpha_composite(sh)
    base.alpha_composite(big, (int(cx - big.width / 2), int(ground - big.height - jump)))

PALE_RED = (255, 226, 226)
PALE_GREEN = (220, 246, 228)
PALE_BLUE = (214, 224, 255)

def pixel_check(d, x, y, k, s=14):
    cells = [(0, 2), (1, 3), (2, 4), (3, 3), (4, 2), (5, 1), (6, 0)]
    for c, (gx, gy) in enumerate(cells):
        if c / len(cells) <= k:
            d.rectangle([x + gx * s, y + gy * s, x + gx * s + s + 3, y + gy * s + s + 3], fill=GREENC + (255,))

def step_head(img, d, t, n, l1, l2, hop=0.25):
    s = ease_back((t + 0.15) / 0.4)
    r = int(70 * s)
    block(d, [540 - r, 370 - r, 540 + r, 370 + r], YELLOW, 1, 10)
    f = font(FONT_B, max(10, int(104 * s)))
    bb = d.textbbox((0, 0), n, font=f)
    d.text((540 - (bb[2] - bb[0]) / 2 - bb[0], 370 - (bb[3] - bb[1]) / 2 - bb[1]), n, font=f, fill=INK + (255,))
    a = appear(t, 0.1, 0.3)
    text_c(d, 500 + (1 - a) * 30, l1, font(FONT_B, 96), INK, a, shadow=True)
    text_c(d, 625 + (1 - a) * 30, l2, font(FONT_B, 96), CORAL, a, shadow=True)
    draw_slime(img, 270, 445, 0.4, t, hop=hop, period=0.7)

def _card(path):
    im = Image.open(os.path.join(OUT, "assets", path)).convert("RGB")
    k = im.width / 1080
    im = im.crop((int(232 * k), int(300 * k), int(848 * k), int(1000 * k))).resize((500, 568), Image.LANCZOS)
    return im
CARDS = [_card("app1.png"), _card("app2.png")]

def scene_hook(img, d, t, T):
    text_c(d, 300, "코드 0줄로", font(FONT_B, 120), INK, 1, shadow=True)
    text_c(d, 450, "앱을 만들었어요", font(FONT_B, 110), CORAL, 1, shadow=True)
    a = appear(t, 0.4, 0.3)
    block(d, [200, 650 + (1 - a) * 30, 880, 750 + (1 - a) * 30], YELLOW, a, 8)
    text_c(d, 663 + (1 - a) * 30, "AI한테 시킨 방법 3가지", font(FONT_B, 58), INK, a)
    # real app screens as proof, on screen from frame 1
    k = clamp((t - 1.7) / 0.25)
    card = CARDS[0] if k <= 0 else (CARDS[1] if k >= 1 else Image.blend(CARDS[0], CARDS[1], k))
    x0, y0 = 320, 850
    fr = ImageDraw.Draw(img)
    fr.rectangle([x0 + 10, y0 + 10, x0 + 512 + 10, y0 + 580 + 10], fill=INK + (255,))
    fr.rectangle([x0, y0, x0 + 512, y0 + 580], fill=INK + (255,))
    img.paste(card, (x0 + 6, y0 + 6))
    draw_slime(img, 170, 1430, 0.5, t + 0.2, hop=1.0, period=0.8)

def scene_step1(img, d, t, T):
    step_head(img, d, t, "1", "만들고 싶은 걸", "말로 설명해요", hop=1.0 if t > 2.1 else 0.25)
    a = appear(t, 0.35, 0.3)
    block(d, [90, 850, 850, 1010], WHITE, a)
    msg = "약 먹을 시간 알려주는 앱 만들어줘"
    n = int(clamp((t - 0.5) / 1.2) * len(msg))
    if a > 0 and n > 0:
        d.text((125, 896), msg[:n], font=font(FONT_M, 46), fill=INK + (255,))
        if n < len(msg):
            bb = d.textbbox((125, 896), msg[:n], font=font(FONT_M, 46))
            d.rectangle([bb[2] + 6, 898, bb[2] + 12, 958], fill=INK + (255,))
    text_c(d, 795, "나", font(FONT_M, 40), SOFT, a, x=96)
    a2 = appear(t, 2.0, 0.3)
    text_c(d, 1065, "AI", font(FONT_M, 40), SOFT, a2, x=96)
    block(d, [90, 1120, 640, 1260], PALE_BLUE, a2)
    if a2 > 0:
        d.text((130, 1156), "네, 만들어 볼게요!", font=font(FONT_M, 50), fill=INK + (int(255 * a2),))
    text_c(d, 1350, "코드 말고 하고 싶은 걸 말해요", font(FONT_M, 50), S_SHADE, appear(t, 2.7), x=96)

ASKS = ["알림 화면 만들어줘", "기록 화면 만들어줘", "달력도 넣어줘"]

def scene_step2(img, d, t, T):
    hop = 0.25
    for i in range(3):
        st = 0.35 + i * 0.85
        if st + 0.4 <= t <= st + 1.1:
            hop = 1.0
    step_head(img, d, t, "2", "작게 쪼개서", "하나씩 시켜요", hop=hop)
    for i, s in enumerate(ASKS):
        st = 0.35 + i * 0.85
        ai = appear(t, st, 0.3)
        y = 840 + i * 170
        x0 = 100 + (1 - ai) * -120
        block(d, [x0, y, x0 + 750, y + 130], WHITE, ai)
        if ai > 0:
            d.text((x0 + 45, y + 34), s, font=font(FONT_M, 52), fill=INK + (int(255 * ai),))
        k = clamp((t - st - 0.4) / 0.25)
        if k > 0:
            pixel_check(d, x0 + 625, y + 28, k)
    text_c(d, 1370, "한 번에 다 시키면 꼬여요", font(FONT_M, 50), S_SHADE, appear(t, 3.0), x=106)

def scene_step3(img, d, t, T):
    step_head(img, d, t, "3", "에러가 나면", "그대로 붙여넣어요", hop=1.0 if t > 1.95 else 0.2)
    a = appear(t, 0.35, 0.3)
    block(d, [100, 850, 850, 1000], PALE_RED, a)
    if a > 0:
        d.text((145, 892), "Error: 뭔지 모를 빨간 글씨", font=font(FONT_M, 48), fill=(200, 60, 60, int(255 * a)))
    la = appear(t, 1.05, 0.3)
    if la > 0:
        c = INK + (int(255 * la),)
        d.rectangle([469, 1030, 481, 1030 + 60 * la], fill=c)
        if la >= 1:
            d.polygon([(451, 1090), (499, 1090), (475, 1114)], fill=c)
    a2 = appear(t, 1.55, 0.3)
    block(d, [100, 1140, 850, 1290], PALE_GREEN, a2)
    if a2 > 0:
        d.text((145, 1180), "AI가 알아서 고쳐줘요", font=font(FONT_M, 52), fill=INK + (int(255 * a2),))
        pixel_check(d, 725, 1176, clamp((t - 1.95) / 0.25))
    text_c(d, 1370, "이해 못 해도 괜찮아요", font(FONT_M, 50), S_SHADE, appear(t, 2.5), x=106)

def scene_cta(img, d, t, T):
    a1 = appear(t, 0.1, 0.3); a3 = appear(t, 1.3, 0.3)
    draw_slime(img, W / 2, 760, 0.95, t, hop=1.0, period=0.7)
    text_c(d, 860, "앱 만들고 싶다던", font(FONT_B, 80), INK, a1, shadow=True)
    text_c(d, 965, "친구에게 보내주세요", font(FONT_B, 78), CORAL, a1, shadow=True)
    text_c(d, 1150, "제가 만든 앱은 프로필에 있어요", font(FONT_R, 44), SOFT, a3)

SCENES = [("s1", scene_hook, 3.6), ("s2", scene_step1, 3.9), ("s3", scene_step2, 4.3), ("s4", scene_step3, 3.9), ("s5", scene_cta, 3.4)]

def frame(fn, t, T, gt):
    img = Image.new("RGBA", (W, H), SKY + (255,))
    draw_bg(img, gt)
    bg_only = img.copy()
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fn(img, ImageDraw.Draw(ov), t, T)
    img.alpha_composite(ov)
    fade = min(1.0 if fn is scene_hook else clamp(t / 0.2), clamp((T - t) / 0.2))
    if fade < 1:
        img = Image.blend(bg_only, img, fade)
    hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(hl).text((60, 130), "honu_dev", font=font(FONT_M, 40), fill=INK + (140,)); img.alpha_composite(hl)
    return img.convert("RGB")

def render(stills=False):
    gt0 = 0.0
    for name, fn, T in SCENES:
        if stills:
            frame(fn, T - 0.6, T, gt0 + T - 0.6).save(os.path.join(OUT, f"v5_still_{name}.jpg"), quality=88)
            if name == 's1': frame(fn, 0.0, T, 0.0).save(os.path.join(OUT, 'v5_still_s0.jpg'), quality=88)
            gt0 += T; continue
        tmp = os.path.join(OUT, f"v5_{name}.tmp.mp4")
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
        for i in range(int(round(T * FPS))):
            p.stdin.write(frame(fn, i / FPS, T, gt0 + i / FPS).tobytes())
        p.stdin.close()
        if p.wait() == 0:
            os.replace(tmp, os.path.join(OUT, f"v5_{name}.mp4"))
        gt0 += T

if __name__ == "__main__":
    render(stills=len(sys.argv) > 1)
