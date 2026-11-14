"""릴스: 코딩 처음인 직장인이 6주 만에 앱 출시 (퀘스트형, 27초 = 54박)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *

SLUG = "pm-app-six-weeks"
G = 232                      # 땅 높이
B = lambda b: int(round(b * BEAT))
T_HOOK, T_PROB, T_Q1, T_Q2, T_Q3, T_CLEAR, T_CTA, T_END = (B(x) for x in (0, 4, 10, 20, 30, 40, 48, 54))
TOTAL = T_END
SX, BX, MX = 38, 92, 118    # 슬라임, 로봇, 모니터의 화면 위치
CAM_PROB, STEP = 400, 180
CAM_END = CAM_PROB + STEP * 3
PHX, PHY = 140, 166
EV = []                      # (프레임, 효과음, 변형)
def ev(fr, name, k=0): EV.append((fr, name, k))

TXT = {
    "hook": ["코딩 처음인 직장인", "*6주 만에 앱 출시*"],
    "prob": ["코딩은 하나도", "모르는데…"],
    "q1": ["AI한테 역할을", "*나눠서* 맡겨요"],
    "q2": ["막히는 화면은", "*캡처*해 보여줘요"],
    "q3": ["알리는 일도", "AI랑 *같이* 해요"],
    "clear": ["6주 만에", "*앱스토어 출시!*"],
    "cta": ["앱 만들고 싶은", "*친구에게* 보내주세요"],
}
for k, ls in TXT.items():
    for l in ls: assert text_w(l, True) <= 150, (k, l, text_w(l, True))

def type_ev(t0, key):
    n = sum(nchars(l) for l in TXT[key])
    for i in range(0, n, 2): ev(t0 + int(i * 1.5), "tick")

def hud(img, f, step, done, t_done=None):
    pill(img, 44, 40, f"퀘스트 {step}/3")
    d = ImageDraw.Draw(img)
    for i in range(3):
        x = 132 + i * 13
        ok = i < done or (i == done and t_done is not None and f >= t_done)
        pop = -2 if (i == done and t_done is not None and 0 <= f - t_done < 3) else 0
        rrect(d, x, 43 + pop, 11, 11, INK)
        d.rectangle([x + 1, 44 + pop, x + 9, 52 + pop], fill=A(GREEN if ok else (YELLOW if i == step - 1 and (f // 8) % 2 else BOX)))
        if ok: put(img, CHECK, x + 2, 45 + pop)

def travel(f, t0):
    """장면 사이 이동: 2박 동안 두 번 뛰며 한 화면(180칸) 전진."""
    p = (f - t0) / B(2)
    if p < 0: return 0, None
    if p >= 1: return STEP, None
    return int(round(STEP * (p * p * (3 - 2 * p)))), hop((p * 2) % 1, 14)

def joy(f, t0, period=B(2), height=24):
    q = ((f - t0) % period) / period
    return hop(q * 1.6, height) if q < 0.625 else None

def card(img, cx, cy, w, h, lines, c2=GREY):
    d = ImageDraw.Draw(img)
    rrect(d, cx - w // 2 - 1, cy - h // 2 - 1, w + 2, h + 2, INK); d.rectangle([cx - w // 2, cy - h // 2, cx + w // 2 - 1, cy + h // 2 - 1], fill=A(CREAM))
    for i in range(lines):
        y = cy - h // 2 + 3 + i * 4
        d.rectangle([cx - w // 2 + 3, y, cx + w // 2 - (4 if i % 2 == 0 else 8), y + 1], fill=A(c2 if i else RED))

def scr_code(l):
    def scr(d, sx, sy):
        for i in range(7):
            w = [30, 16, 38, 24, 34, 12, 28][(i + l // 6) % 7]
            d.rectangle([sx + 4 + (i % 3) * 3, sy + 3 + i * 4, sx + 4 + (i % 3) * 3 + w, sy + 4 + i * 4], fill=A(RED if (i + l // 6) % 4 == 1 else GREEN))
    return scr
def scr_ok(img):
    def scr(d, sx, sy):
        rrect(d, sx + 14, sy + 6, 22, 20, GREEN); img.alpha_composite(CHECK, (sx + 22, sy + 13))
    return scr

def frame(f):
    shake = (0, 0)
    # ---------- 훅 (현재: 이미 출시함) ----------
    if f < T_PROB:
        img = background(f, CAM_END)
        put_bot(img, BX, G, f, on=(f // 8) % 2 == 0)
        put_slime(img, SX, G, f, "happy", jump=joy(f, 0))
        py = PHY + [0, 1, 2, 1][(f // 8) % 4]
        phone(img, PHX, py); sparkle(img, PHX, py, f, 26, STAR_Y)
        dialog(img, TXT["hook"], None)
        if f >= B(1): pill(img, 90, 104, "따라 할 방법 3가지", dy=[4, -2, -1][f - B(1)] if f - B(1) < 3 else 0)
        blinds(img, f - (T_PROB - 7))
        return img
    # ---------- 6주 전: 문제 ----------
    if f < T_Q1:
        l = f - T_PROB
        img = background(f, CAM_PROB)
        monitor(img, MX, G, scr_code(l))
        drop = B(4.5)
        if l >= drop - 6:
            put_bot(img, BX, G + min(0, -(drop - l) * 32), f)
            dust(img, BX, G, l - drop)
            if l in (drop, drop + 1, drop + 2): shake = ((1, -1, 0)[l - drop], (2, -1, 1)[l - drop])
        face = "wow" if l >= drop - 2 else ("sad" if l >= B(1) else "base")
        slump = B(1.5) <= l < drop - 2
        put_slime(img, SX, G, f, face, 1, jump=(0, 52, 31) if slump else None)
        for i, (qx, qy, qt) in enumerate(((20, 176, B(1)), (38, 166, B(1.5)), (56, 176, B(2)))):
            if qt <= l < drop - 2: draw_text(img, qx, qy - min(3, (l - qt) // 2) + ((f // 10 + i) % 2), "?", YELLOW, True)
        if l >= drop: draw_text(img, SX + 16, 178, "!", YELLOW, True)
        pill(img, 34, 40, "6주 전")
        dialog(img, TXT["prob"], l - 6 if l >= 6 else -99)
        blinds(img, 6 - l)
        return _shake(img, shake)
    # ---------- 퀘스트 1~3 ----------
    if f < T_CLEAR:
        qi = (f - T_Q1) // B(10)
        t0 = T_Q1 + qi * B(10); l = f - t0
        dx, tj = travel(f, t0)
        img = background(f, CAM_PROB + qi * STEP + dx)
        moving = tj is not None
        t_ok = t0 + B(7.5)
        happy = f >= t_ok
        sj = tj or (hop((f - t_ok) / B(1.2), 22) if happy and f - t_ok < B(1.2) else None)
        bot_on = False
        bot_jump = hop(((l / B(1)) - 0.3) % 1, 8)[0] if moving and l > 4 else 0
        d = ImageDraw.Draw(img); late = []
        if qi == 0:
            if dx < STEP: monitor(img, MX - dx, G, scr_code(l))
            drop = B(2.5); B2 = 150
            if l >= drop - 6:
                put_bot(img, B2, G + min(0, -(drop - l) * 32), f, on=l >= B(5.5), jump=hop((l - B(5.5)) / 10, 6)[0] if l >= B(5.5) else 0)
                dust(img, B2, G, l - drop)
                if l in (drop, drop + 1): shake = (0, (2, -1)[l - drop])
            if l >= B(4): bot_on = True; bot_jump = hop((l - B(4)) / 10, 6)[0]
            late.append(lambda: bubble(img, BX, 182, "설계 담당", BX, l - B(4)))
            late.append(lambda: bubble(img, 142, 160, "검토 담당", B2, l - B(5.5)))
        if qi == 1:
            if dx < STEP: put_bot(img, 150 - dx, G, f, on=True)
            pressed = l >= B(7.5)
            mx = MX + STEP - dx
            def scr(d, sx, sy):
                if pressed: return scr_ok(img)(d, sx, sy)
                for i in range(3):
                    hl = l >= B(5.5) and i == 1 and (l // 6) % 2 == 0
                    rrect(d, sx + 4, sy + 3 + i * 10, 28, 7, YELLOW if hl else GREY)
                if l < B(5.5): draw_text(img, sx + 36, sy + 9, "?", RED, True)
                elif (l // 6) % 2 == 0: draw_text(img, sx + 35, sy + 10, "<", YELLOW, True)
            monitor(img, mx, G, scr)
            fl = l - B(3.5)
            if 4 <= fl < 16:          # 캡처 카드가 포물선으로 로봇에게 날아간다
                p = (fl - 4) / 12
                card(img, int(146 + (BX - 146) * p), int(190 - 30 * 4 * p * (1 - p) + 10 * p), 17, 13, 2)
            if fl >= 16: bot_on = True
            if 16 <= fl < 26: bot_jump = hop((fl - 16) / 10, 6)[0]
            late.append(lambda: bubble(img, 66, 180, "이 버튼 눌러요", BX, l - B(5.5)))
            if B(2.5) <= l < B(3.5): draw_text(img, SX + 16, 178 - min(3, (l - B(2.5)) // 2), "?", YELLOW, True)
        if qi == 2:
            if dx < STEP: monitor(img, MX - dx, G, scr_ok(img))
            if B(2.5) <= l < B(5): bubble(img, 50, 170, "소개 글 써줘", SX + 6, l - B(2.5))
            if l >= B(4): bot_on = True
            if B(4) <= l < B(5): bot_jump = (l // 3) % 2
            pt = l - B(5)
            if pt >= 0:               # 글이 종이가 되어 올라가 게시물이 된다
                p = min(1, pt / 10)
                cx = int(BX + (140 - BX) * p); cy = int(200 + (168 - 200) * p - 12 * 4 * p * (1 - p))
                if pt < 10: card(img, cx, cy, 13, 15, 3)
                else: card(img, 140, 168 + ((f // 10) % 2), 31, 37, 8)
                for i in range(3):
                    ht = pt - 14 - i * 7
                    if ht >= 0: put(img, HEART, (164, 110, 152)[i] - 4, (150, 160, 132)[i] - min(8, ht) + ((f // 8 + i) % 2))
        put_bot(img, BX, G, f, on=bot_on, jump=bot_jump)
        face = "happy" if happy else ("wow" if (qi == 1 and B(2.5) <= l < B(5.5)) else "base")
        put_slime(img, SX, G, f, face, 1, jump=sj)
        if moving and tj[0] == 0 and l > 3: dust(img, SX, G, 3)
        for fn in late: fn()
        if qi == 1 and 0 <= l - B(3.5) < 4:     # 찰칵
            k = l - B(3.5)
            if k < 2: d.rectangle([0, 0, LW, LH], fill=A(WHITE))
            else:
                for r in ([0, 0, LW, 5], [0, LH - 6, LW, LH], [0, 0, 4, LH], [LW - 5, 0, LW, LH]): d.rectangle(r, fill=A(WHITE))
        hud(img, f, qi + 1, qi, t_ok)
        dialog(img, TXT["q%d" % (qi + 1)], l - 4 if l >= 4 else -99)
        return _shake(img, shake)
    # ---------- 퀘스트 완료 → 마무리 ----------
    l = f - T_CLEAR
    cta = f >= T_CTA
    img = background(f if l >= 3 else T_CLEAR, CAM_END)      # 처음 3프레임은 멈춤(히트스톱)
    put_bot(img, BX, G, f, on=True, jump=hop(((l - 8) % B(2)) / B(2) * 1.6, 10)[0] if l >= 8 and not cta else 0)
    put_slime(img, SX, G, f, "happy", jump=joy(f, T_CLEAR + 3) if l >= 3 else (0, 52, 31))
    py = PHY + [0, 1, 2, 1][(f // 8) % 4]
    fall = min(0, -(B(1.5) - l) * 14)
    if l >= 3:
        phone(img, PHX, py + fall)
        if fall == 0: sparkle(img, PHX, py, f, 26, STAR_Y)
    d = ImageDraw.Draw(img)
    if l >= 3 and l < B(8) + B(1):          # 색종이
        r = random.Random(11)
        for i in range(30):
            x0, sp, ph = r.randrange(4, LW - 6), r.choice((2, 3, 4)), r.randrange(0, 120)
            y = 100 + (l - 3) * sp - ph
            if 104 <= y < 228:
                x = x0 + ((l // 5 + i) % 3 - 1) * 2
                d.rectangle([x, y, x + 2, y + 2], fill=A((YELLOW, RED, GREEN, CREAM)[i % 4]))
    if not cta:
        by = [-30, -12, 3, -1, 0][l - 3] if 3 <= l < 8 else 0
        if l >= 3: pill(img, 90, 40, "QUEST CLEAR!", dy=by)
        if l in (5, 6, 7, 8): shake = ((2, -2, 1, 0)[l - 5], (-2, 2, -1, 1)[l - 5])
        if l < 2: d.rectangle([0, 0, LW, LH], fill=A(WHITE))
        dialog(img, TXT["clear"], l - 8 if l >= 8 else -99)
        if l >= B(3.5): pill(img, 90, 104, "Anthropic 블로그 사례", fill=CREAM, bold=False, dy=[3, -1][l - B(3.5)] if l - B(3.5) < 2 else 0)
    else:
        dialog(img, TXT["cta"], f - T_CTA)
    return _shake(img, shake)

def _shake(img, s):
    if s == (0, 0): return img
    out = Image.new("RGBA", img.size, A(INK)); out.paste(img, s); return out

# ---------- 효과음 박자표 ----------
ev(B(1), "pop"); ev(0, "jump"); ev(B(2), "jump")
ev(T_PROB - 7, "whoosh"); ev(T_PROB + B(1), "error"); type_ev(T_PROB + 6, "prob")
ev(T_PROB + B(4.5) - 6, "drop"); ev(T_PROB + B(4.5), "land")
for qi, t0 in enumerate((T_Q1, T_Q2, T_Q3)):
    ev(t0, "jump"); ev(t0 + B(1), "jump"); ev(t0 + B(1) - 2, "land"); ev(t0 + B(2) - 2, "land")
    type_ev(t0 + 4, "q%d" % (qi + 1)); ev(t0 + B(7.5), "check"); ev(t0 + B(7.5) + 2, "jump")
ev(T_Q1 + B(2.5) - 6, "drop"); ev(T_Q1 + B(2.5), "land"); ev(T_Q1 + B(4), "pop"); ev(T_Q1 + B(5.5), "pop", 2)
ev(T_Q2 + B(2.5), "error"); ev(T_Q2 + B(3.5), "shutter"); ev(T_Q2 + B(3.5) + 4, "whoosh"); ev(T_Q2 + B(5.5), "pop")
ev(T_Q3 + B(2.5), "pop"); ev(T_Q3 + B(5), "whoosh")
for i in range(3): ev(T_Q3 + B(5) + 14 + i * 7, "pop", i + 1)
ev(T_CLEAR + 3, "fanfare"); ev(T_CLEAR + 5, "land"); ev(T_CLEAR + B(1.5), "check"); type_ev(T_CLEAR + 8, "clear"); ev(T_CLEAR + B(3.5), "pop")
type_ev(T_CTA, "cta")

def plan(b):
    if b < 4: return ((0, False, 1.0), (7, False, 1.0))[b // 2 % 2]          # C G
    if b < 9: return ((9, True, 0.5), (5, False, 0.5))[(b - 4) // 2 % 2]      # Am F (작게)
    if b < 10: return (7, False, 0.7)
    if b < 40: return ((0, False, 0.8), (7, False, 0.8), (9, True, 0.8), (5, False, 0.8))[(b - 10) // 2 % 4]
    return ((0, False, 1.0), (5, False, 1.0), (7, False, 1.0), (0, False, 1.0))[(b - 40) // 2 % 4]

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", SLUG); os.makedirs(out, exist_ok=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else "video"
    if mode == "stills":
        fr = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else list(range(0, TOTAL, 15))
        ims = [frame(f).convert("RGB") for f in fr]
        cols = 9; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * LW * 2, rows * LH * 2), INK)
        for i, im in enumerate(ims): sheet.paste(im.resize((LW * 2, LH * 2), Image.NEAREST), ((i % cols) * LW * 2, (i // cols) * LH * 2))
        sheet.save(os.path.join(out, "sheet.png")); print("sheet", len(ims))
    else:
        for name, bgm in (("reel", music(54, plan)), ("reel_sfx_only", None)):
            wav = os.path.join(out, name + ".wav"); write_wav(wav, mix(TOTAL, EV, bgm))
            render(frame, TOTAL, os.path.join(out, name + ".mp4"), wav, -14 if bgm is not None else -19)
        print("done", TOTAL / FPS, "s")
