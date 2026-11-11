"""honu_dev 릴스 고정 틀: 훅 -> 3단계 -> 마무리.

문구는 JSON 파일에서 읽는다. 장면 코드는 고치지 않는다.
  python3 make_reel.py example.json stills   # 장면별 미리보기 그림만
  python3 make_reel.py example.json          # out/<slug>/reel.mp4 생성
"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw
from slime_base import (W, H, FPS, OUT, FONT_B, FONT_M, FONT_R, INK, YELLOW, CORAL, GREENC, SOFT, WHITE, S_SHADE,
                        font, text_c, block, draw_bg, appear, ease_back, clamp, SKY)

# ---------- 캐릭터: 연한 파랑 픽셀 슬라임 (바꾸지 않는다) ----------
C_OUT = (40, 44, 72)
C_BODY = (150, 208, 255)
ROWS = [
    ".....OOOOOO.....",
    "...OOBBBBBBOO...",
    "..OBWWBBBBBBBO..",
    ".OBWBBBBBBBBBBO.",
    ".OBBBBBBBBBBBBO.",
    "OBBBBBBBBBBBBBBO",
    "OBBBBBBBBBBBBBBO",
    "OBBBBBBBBBBBBBBO",
    "OBBBBBBBBBBBBBBO",
    "OBBBBBBBBBBBBBBO",
    "OBBBBBBBBBBBBBBO",
    "OBBBBBBBBBBBBBBO",
    ".OBBBBBBBBBBBBO.",
    "..OOOOOOOOOOOO..",
]
PAL = {"O": C_OUT, "B": C_BODY, "W": WHITE, "E": (24, 24, 40), "P": (255, 140, 160)}
MOODS = ("base", "surprise", "excited", "smile")

def face(mood, blink):
    """표정별 눈·입 픽셀. base 기본 / surprise 놀람 / excited 신남 / smile 웃음."""
    px = {}
    if mood == "surprise":      # 흰자 안에 작은 눈동자 + 턱에 붙은 세로 입
        for c in (4, 11):
            for y in range(5, 9):
                for x in (c - 1, c, c + 1):
                    px[(x, y)] = "W"
            px[(c, 6)] = "E"; px[(c, 7)] = "E"
        for x in (7, 8):
            for y in (10, 11, 12):
                px[(x, y)] = "E"
    elif mood == "excited":     # 길어진 눈 + 턱에 붙여 크게 벌린 입
        for x0 in (4, 10):
            for y in range(5, 10):
                for x in (x0, x0 + 1):
                    px[(x, y)] = "E"
            px[(x0, 5)] = "W"
        for x in (6, 7, 8, 9):
            for y in (11, 12):
                px[(x, y)] = "E"
        px[(7, 12)] = "P"; px[(8, 12)] = "P"
    elif mood == "smile":       # ^ ^ 눈
        for c in (4, 11):
            px[(c - 1, 8)] = "E"; px[(c, 7)] = "E"; px[(c + 1, 8)] = "E"
    elif blink:                 # 기본 눈 깜빡임
        for x0 in (4, 10):
            px[(x0, 8)] = "E"; px[(x0 + 1, 8)] = "E"
    else:                       # 기본: 검정 세로 눈 + 왼쪽 위 흰 반짝임 한 칸
        for x0 in (4, 10):
            for y in range(6, 10):
                for x in (x0, x0 + 1):
                    px[(x, y)] = "E"
            px[(x0, 6)] = "W"
    return px

def slime_sprite(blink=False, mood="base"):
    im = Image.new("RGBA", (16, len(ROWS)), (0, 0, 0, 0))
    for j, r in enumerate(ROWS):
        for i, ch in enumerate(r):
            if ch != ".":
                im.putpixel((i, j), PAL[ch] + (255,))
    for (x, y), ch in face(mood, blink).items():
        im.putpixel((x, y), PAL[ch] + (255,))
    return im

def get_mood(c):
    m = c.get("mood", "base")
    if m not in MOODS:
        raise SystemExit(f"mood 는 {MOODS} 중 하나여야 합니다: {m}")
    return m

def draw_slime(base, cx, ground, scale, t, hop=1.0, period=0.9, mood="base"):
    ph = (t / period) % 1.0
    air = math.sin(math.pi * ph)
    jump = air * 150 * scale * hop
    land = max(0.0, 1 - ph / 0.14) + max(0.0, (ph - 0.86) / 0.14)
    sq = land * 0.2 * hop; st = air * 0.07 * hop
    spr = slime_sprite((t % 3.0) > 2.85, mood)
    P = 30 * scale
    big = spr.resize((int(16 * P * (1 + sq - st)), int(14 * P * (1 - sq + st))), Image.NEAREST)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sw = int((190 - air * 60 * hop) * scale)
    ImageDraw.Draw(sh).rectangle([cx - sw, ground - 4 * scale, cx + sw, ground + 12 * scale], fill=(34, 32, 64, 40))
    base.alpha_composite(sh)
    base.alpha_composite(big, (int(cx - big.width / 2), int(ground - big.height - jump)))

TONES = {"white": WHITE, "blue": (214, 224, 255), "red": (255, 226, 226), "green": (220, 246, 228)}
_M = ImageDraw.Draw(Image.new("RGB", (8, 8)))

def fit(text, path, size, max_w, min_size):
    """글자가 max_w 안에 들어올 때까지 줄인다. min_size 로도 안 들어가면 멈춘다."""
    while size >= min_size:
        f = font(path, size)
        bb = _M.textbbox((0, 0), text, font=f)
        if bb[2] - bb[0] <= max_w:
            return f
        size -= 4
    raise SystemExit(f"문구가 너무 깁니다 (줄여 주세요): {text}")

def pixel_check(d, x, y, k, s=14):
    cells = [(0, 2), (1, 3), (2, 4), (3, 3), (4, 2), (5, 1), (6, 0)]
    for c, (gx, gy) in enumerate(cells):
        if c / len(cells) <= k:
            d.rectangle([x + gx * s, y + gy * s, x + gx * s + s + 3, y + gy * s + s + 3], fill=GREENC + (255,))

# ---------- 장면 1: 훅 ----------
def make_hook(c, base_dir):
    cards = []
    for p in c.get("images", [])[:2]:
        im = Image.open(os.path.join(base_dir, p)).convert("RGB")
        k = max(500 / im.width, 568 / im.height)
        im = im.resize((int(im.width * k) + 1, int(im.height * k) + 1), Image.LANCZOS)
        x = (im.width - 500) // 2; y = (im.height - 568) // 2
        cards.append(im.crop((x, y, x + 500, y + 568)))
    f1 = fit(c["line1"], FONT_B, 120, 940, 84)
    f2 = fit(c["line2"], FONT_B, 110, 940, 80)
    fb = fit(c["badge"], FONT_B, 58, 620, 44)
    mood = get_mood(c)

    def scene(img, d, t, T):
        text_c(d, 300, c["line1"], f1, INK, 1, shadow=True)
        text_c(d, 450, c["line2"], f2, CORAL, 1, shadow=True)
        a = appear(t, 0.4, 0.3)
        block(d, [200, 650 + (1 - a) * 30, 880, 750 + (1 - a) * 30], YELLOW, a, 8)
        text_c(d, 663 + (1 - a) * 30, c["badge"], fb, INK, a)
        if cards:
            k = clamp((t - 1.7) / 0.25) if len(cards) > 1 else 0
            card = cards[0] if k <= 0 else (cards[1] if k >= 1 else Image.blend(cards[0], cards[1], k))
            x0, y0 = 320, 850
            fr = ImageDraw.Draw(img)
            fr.rectangle([x0 + 10, y0 + 10, x0 + 522, y0 + 590], fill=INK + (255,))
            fr.rectangle([x0, y0, x0 + 512, y0 + 580], fill=INK + (255,))
            img.paste(card, (x0 + 6, y0 + 6))
            draw_slime(img, 170, 1430, 0.5, t + 0.2, hop=1.0, period=0.8, mood=mood)
        else:
            draw_slime(img, 500, 1400, 0.95, t + 0.2, hop=1.0, period=0.8, mood=mood)
    return scene, 3.6

# ---------- 장면 2~4: 단계 ----------
def make_step(n, c):
    boxes = c["boxes"][:3]
    ft1 = fit(c["title1"], FONT_B, 96, 940, 68)
    ft2 = fit(c["title2"], FONT_B, 96, 940, 68)
    fbx = [fit(b["text"], FONT_M, 52, 560 if b.get("check") else 670, 36) for b in boxes]
    fn = fit(c["note"], FONT_M, 50, 740, 36)
    starts = [0.35 + i * 0.85 for i in range(len(boxes))]
    note_at = starts[-1] + 0.9
    mood = get_mood(c)
    T = note_at + 1.6

    def scene(img, d, t, T):
        hop = 0.25
        for st in starts:
            if st + 0.4 <= t <= st + 1.1:
                hop = 1.0
        s = ease_back((t + 0.15) / 0.4)
        r = int(70 * s)
        block(d, [540 - r, 370 - r, 540 + r, 370 + r], YELLOW, 1, 10)
        f = font(FONT_B, max(10, int(104 * s)))
        bb = d.textbbox((0, 0), str(n), font=f)
        d.text((540 - (bb[2] - bb[0]) / 2 - bb[0], 370 - (bb[3] - bb[1]) / 2 - bb[1]), str(n), font=f, fill=INK + (255,))
        a = appear(t, 0.1, 0.3)
        text_c(d, 500 + (1 - a) * 30, c["title1"], ft1, INK, a, shadow=True)
        text_c(d, 625 + (1 - a) * 30, c["title2"], ft2, CORAL, a, shadow=True)
        draw_slime(img, 270, 445, 0.4, t, hop=hop, period=0.7, mood=mood if t >= starts[-1] + 0.3 else "base")
        for i, b in enumerate(boxes):
            ai = appear(t, starts[i], 0.3)
            y = 840 + i * 170
            x0 = 100 - (1 - ai) * 120
            block(d, [x0, y, x0 + 750, y + 130], TONES.get(b.get("tone", "white"), WHITE), ai)
            if ai > 0:
                bb = d.textbbox((0, 0), b["text"], font=fbx[i])
                d.text((x0 + 45, y + 65 - (bb[3] + bb[1]) / 2), b["text"], font=fbx[i], fill=INK + (int(255 * ai),))
            if b.get("check"):
                k = clamp((t - starts[i] - 0.4) / 0.25)
                if k > 0:
                    pixel_check(d, x0 + 625, y + 28, k)
        text_c(d, 1370, c["note"], fn, S_SHADE, appear(t, note_at), x=106)
    return scene, round(T, 2)

# ---------- 장면 5: 마무리 ----------
def make_cta(c):
    f1 = fit(c["line1"], FONT_B, 80, 940, 60)
    f2 = fit(c["line2"], FONT_B, 78, 940, 60)
    f3 = fit(c.get("small", ""), FONT_R, 44, 900, 34) if c.get("small") else None
    mood = get_mood(c)

    def scene(img, d, t, T):
        a1 = appear(t, 0.1, 0.3)
        draw_slime(img, W / 2, 760, 0.95, t, hop=1.0, period=0.7, mood=mood)
        text_c(d, 860, c["line1"], f1, INK, a1, shadow=True)
        text_c(d, 965, c["line2"], f2, CORAL, a1, shadow=True)
        if f3:
            text_c(d, 1150, c["small"], f3, SOFT, appear(t, 1.3, 0.3))
    return scene, 3.4

def frame(fn, t, T, gt, first):
    img = Image.new("RGBA", (W, H), SKY + (255,))
    draw_bg(img, gt)
    bg_only = img.copy()
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fn(img, ImageDraw.Draw(ov), t, T)
    img.alpha_composite(ov)
    fade = min(1.0 if first else clamp(t / 0.2), clamp((T - t) / 0.2))
    if fade < 1:
        img = Image.blend(bg_only, img, fade)
    hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(hl).text((60, 130), "honu_dev", font=font(FONT_M, 40), fill=INK + (140,))
    img.alpha_composite(hl)
    return img.convert("RGB")

def main(path, stills):
    with open(path, encoding="utf-8") as fh:
        c = json.load(fh)
    if len(c["steps"]) != 3:
        raise SystemExit("steps 는 정확히 3개여야 합니다")
    base_dir = os.path.dirname(os.path.abspath(path))
    scenes = [make_hook(c["hook"], base_dir)] + [make_step(i + 1, s) for i, s in enumerate(c["steps"])] + [make_cta(c["cta"])]
    out = os.path.join(OUT, "out", c["slug"])
    os.makedirs(out, exist_ok=True)
    gt0 = 0.0; parts = []
    for i, (fn, T) in enumerate(scenes):
        if stills:
            if i == 0:
                frame(fn, 0.0, T, 0.0, True).save(os.path.join(out, "still_0.jpg"), quality=88)
            frame(fn, T - 0.6, T, gt0 + T - 0.6, i == 0).save(os.path.join(out, f"still_{i + 1}.jpg"), quality=88)
            gt0 += T; continue
        tmp = os.path.join(out, f"s{i + 1}.tmp.mp4"); dst = os.path.join(out, f"s{i + 1}.mp4")
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
        for k in range(int(round(T * FPS))):
            p.stdin.write(frame(fn, k / FPS, T, gt0 + k / FPS, i == 0).tobytes())
        p.stdin.close()
        if p.wait() != 0:
            raise SystemExit(f"장면 {i + 1} 만들기 실패")
        os.replace(tmp, dst); parts.append(dst); gt0 += T
    if stills:
        print("미리보기:", out, "/ 길이", round(gt0, 1), "초"); return
    lst = os.path.join(out, "list.txt")
    with open(lst, "w") as fh:
        fh.writelines(f"file '{p}'\n" for p in parts)
    final = os.path.join(out, "reel.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", final], check=True)
    print("완성:", final, "/ 길이", round(gt0, 1), "초")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("사용법: python3 make_reel.py <문구.json> [stills]")
    main(sys.argv[1], len(sys.argv) > 2)
