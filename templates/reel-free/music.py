"""TENBY LABS 릴스 배경음 + 효과음 생성기 (코드로 직접 만들어 저작권 걱정 없음).

기준 분위기: 채널 주인이 고른 큐트 카와이 로파이(Heart Bubbles, tenbylabs 릴스에 쓴 lemonade·chocolate milk·pudding 등).
  2026-11-23 "축축 처진다" 피드백 + 그 곡들을 측정한 값 반영: 빠른 박 130~150(드럼은 절반 속도), 촘촘한 타격, G·D장조, 장조, 짧게 끊어 치는 피아노, 톡톡 튀는 플럭·오르골 멜로디,
  통통 튀는 베이스, 박수 섞인 스네어와 촘촘한 하이햇, 따뜻하지만 답답하지 않은 소리.
남의 곡의 멜로디·화음 진행을 베끼지 않는다. 멜로디는 매번 seed 로 새로 만든다.

python3 music.py --dur 48.6 --mood bright --seed <slug> --events events.json --out out/audio.wav
  --mood   calm(차분) | bright(밝음, 기본) | playful(통통 튐) | focus(주의·진지)
  --events 효과음 목록 JSON: [[초, "종류"], ...] 또는 [[초, "종류", 값], ...]
           종류: drop(떨어짐) land(착지) pop(글자 등장) sparkle(반짝 퍼짐) whoosh_out(뛰어나감) whoosh_in(들어옴)
                 thud(카드·물건 놓임) jump(점프) stamp(도장) stamp_big(큰 도장+흔들림) tick(숫자, 값=몇 번째)
                 alert(경고) check(체크, 값=몇 번째) riser(줌인·고조) chime(마무리) type(타자 한 번) swipe(넘김)
  --music-only / --sfx-only 로 따로 뽑을 수도 있다.
python3 music.py ... 후 영상과 합치기:
  ffmpeg -y -i out/reel.mp4 -i out/audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest out/reel_sound.mp4
"""
import argparse, json, hashlib
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100

def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)

def add(buf, t, sig, g=1.0):
    i = int(round(t * SR))
    if i >= len(buf) or i + len(sig) <= 0: return
    a = max(0, -i); i = max(0, i)
    j = min(len(buf), i + len(sig) - a)
    buf[i:j] += sig[a:a + j - i] * g

def adsr(n, a, d, s, r, hold):
    e = np.zeros(n); ai, di, ri = int(a * SR), int(d * SR), int(r * SR)
    hold = min(hold, n); hi = max(hold - ai - di, 0)
    seg = np.concatenate([np.linspace(0, 1, ai, False), np.linspace(1, s, di, False), np.full(hi, s), np.linspace(s, 0, ri)])
    e[:min(n, len(seg))] = seg[:n]; return e

# ---------------- 악기 ----------------
def piano(m, dur, vel, rng):
    """부드러운 펠트 피아노: 배음마다 따로 줄어드는 감쇠 + 줄 두 개 살짝 어긋남 + 망치 소리."""
    n = int((dur + 1.2) * SR); t = np.arange(n) / SR; f = hz(m)
    out = np.zeros(n)
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + 0.00035 * k * k)
        if fk > 6000: break
        amp = (1 / k ** 1.25) * np.exp(-t * (0.9 + 0.75 * k))
        det = 1 + (0.0006 if k % 2 else -0.0005)
        out += amp * (np.sin(2 * np.pi * fk * t) + 0.6 * np.sin(2 * np.pi * fk * det * t + 1.3))
    ham = lp(rng.standard_normal(int(0.012 * SR)), 1800) * 0.25
    out[:len(ham)] += ham
    rel = np.ones(n); ri = int(dur * SR)
    if ri < n: rel[ri:] = np.exp(-np.arange(n - ri) / SR * 9)
    return lp(out * rel, 2400 + vel * 1200) * vel * 0.22

def musicbox(m, vel):
    n = int(1.6 * SR); t = np.arange(n) / SR; f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 6) + 0.12 * np.sin(2 * np.pi * 4.07 * f * t) * np.exp(-t * 12)
    return lp(s * np.exp(-t * 3.2) * np.minimum(1, t * 400), 3800) * vel * 0.16

def pluck(m, vel):
    """마림바·칼림바처럼 톡 끊어지는 소리 (멜로디용, 통통 튀는 느낌)."""
    n = int(0.5 * SR); t = np.arange(n) / SR; f = hz(m)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 9) + 0.5 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 30) + 0.2 * np.sin(2 * np.pi * 10 * f * t) * np.exp(-t * 60)
    return lp(s * np.minimum(1, t * 800), 7000) * vel * 0.2

def clap(rng):
    n = int(0.18 * SR); t = np.arange(n) / SR; x = hp(rng.standard_normal(n), 1200)
    e = np.exp(-t * 30) + 0.6 * np.exp(-np.maximum(t - 0.012, 0) * 30) * (t > 0.012)
    return lp(x * e, 6000) * 0.25

def bass(m, dur):
    n = int((dur + 0.15) * SR); t = np.arange(n) / SR; f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.18 * np.sin(2 * np.pi * 2 * f * t)
    s = np.tanh(1.6 * s) / np.tanh(1.6)
    return lp(s * adsr(n, 0.01, 0.2, 0.75, 0.12, int(dur * SR)), 600) * 0.34

def kick(rng):
    n = int(0.32 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(48 + 70 * np.exp(-t * 28)) / SR) * np.exp(-t * 11) * 0.9
def snare(rng):
    n = int(0.25 * SR); t = np.arange(n) / SR
    return lp(hp(rng.standard_normal(n), 900), 3200) * np.exp(-t * 18) * 0.35 + np.sin(2 * np.pi * 185 * t) * np.exp(-t * 26) * 0.25
def rim(rng):
    n = int(0.06 * SR); t = np.arange(n) / SR
    return lp(np.sin(2 * np.pi * 900 * t) + 0.5 * rng.standard_normal(n), 2600) * np.exp(-t * 70) * 0.25
def shaker(rng):
    n = int(0.07 * SR); t = np.arange(n) / SR
    return lp(hp(rng.standard_normal(n), 6000), 11000) * np.exp(-t * 60) * 0.12

# ---------------- 분위기별 설정 (진행은 흔한 재즈·로파이 화성 문법으로 직접 짠 것) ----------------
CH = {  # 근음(미디)과 구성음(근음 기준 반음)
    'Cmaj9': (48, [0, 4, 7, 11, 14]), 'Am9': (45, [0, 3, 7, 10, 14]), 'Dm9': (50, [0, 3, 7, 10, 14]),
    'G6': (43, [0, 4, 7, 9, 14]), 'Fmaj9': (41, [0, 4, 7, 11, 14]), 'Em7': (40, [0, 3, 7, 10, 14]),
    'G13sus': (43, [0, 5, 7, 10, 16]), 'E7b9': (40, [0, 4, 7, 10, 13]), 'Fm6': (41, [0, 3, 7, 9, 14]),
    'Bbmaj7': (46, [0, 4, 7, 11, 14]), 'D9': (50, [0, 4, 7, 10, 14]),
}
MOODS = {  # 2026-11-23 채널 주인 릴스에 쓴 곡 6개를 측정한 값에 맞춤:
    # 빠른 박 130~150(드럼은 그 절반으로 느긋하게), 1초에 3.4~4.9번 촘촘한 타격, G·D장조 중심, 두툼한 저음, 고음은 적게
    'calm':    dict(bpm=132, key=7, progs=[['Fmaj9', 'G6', 'Em7', 'Am9'], ['Cmaj9', 'Am9', 'Fmaj9', 'G6']], mel=0.45, drums=0.85, box=0.9, hats16=False),
    'bright':  dict(bpm=140, key=7, progs=[['Cmaj9', 'Am9', 'Fmaj9', 'G6'], ['Fmaj9', 'G6', 'Em7', 'Am9']], mel=0.6, drums=1.0, box=1.0, hats16=True),
    'playful': dict(bpm=146, key=2, progs=[['Fmaj9', 'G6', 'Cmaj9', 'Am9'], ['Cmaj9', 'D9', 'Fmaj9', 'G6']], mel=0.7, drums=1.1, box=1.15, hats16=True),
    'focus':   dict(bpm=136, key=9, progs=[['Am9', 'Fmaj9', 'Cmaj9', 'G6'], ['Dm9', 'G13sus', 'Cmaj9', 'Am9']], mel=0.45, drums=0.95, box=0.85, hats16=False),
}
PENTA = [0, 2, 4, 7, 9]  # 장조 펜타토닉

def key_of(mood):
    k = MOODS[mood]['key']; return k - 12 if k > 6 else k

TONAL = {'pop', 'sparkle', 'tick', 'alert', 'check', 'chime', 'stamp'}  # 음 높이가 있는 효과음

def make_music(dur, mood, seed, avoid=()):
    P = MOODS[mood]; rng = np.random.default_rng(seed)
    beat = 60 / P['bpm']; bar = 4 * beat; sw = 0.56
    KEY = key_of(mood)   # 조 옮기기(G=-5, D=+2, A=-3)
    n = int((dur + 2) * SR)
    keys, bs, dr, mel = (np.zeros(n) for _ in range(4))
    prog = P['progs'][rng.integers(len(P['progs']))]
    nbars = int(np.ceil(dur / bar)) + 1
    intro = min(1.0, dur * 0.04)
    kenv = np.zeros(n)
    for b in range(nbars):
        t0 = b * bar; root, iv = CH[prog[(b // 2) % 4]]   # 화음은 2마디마다(빠른 박 기준)
        root += KEY
        voic = [root + 12 + i for i in iv[1:]]
        while min(voic) < 58: voic = [v + 12 for v in voic]
        while max(voic) > 79: voic = [v - 12 for v in voic]
        # 피아노: 짧게 콕콕 (빠른 박에서 1, 2&, 4)
        for hit, ln, vel in ((0, 0.9, 0.6), (1.5, 0.5, 0.45), (3.0, 0.5, 0.42)):
            if b % 2 == 1 and hit == 0: vel *= 0.8
            for k, m in enumerate(sorted(voic)):
                add(keys, t0 + hit * beat + k * 0.006, piano(m, beat * ln, vel + rng.uniform(-.05, .05), rng))
        # 두툼한 저음(808처럼 둥글게): 2마디에 한 번 길게 + 중간에 짧게
        if t0 >= intro - 0.01:
            if b % 2 == 0:
                add(bs, t0, bass(root - 12 if root > 40 else root, bar * 1.2) * 1.2)
            else:
                add(bs, t0 + 2.5 * beat, bass(root + 7 - (12 if root > 40 else 0), beat * 1.0))
                add(bs, t0 + 3.5 * beat, bass(root + 12 - (12 if root > 40 else 0), beat * 0.4))
    K, S, C, R, Sh = kick(rng), snare(rng), clap(rng), rim(rng), shaker(rng)
    ke = np.exp(-np.arange(int(.25 * SR)) / SR * 14)
    nb = int(dur / beat) + 2
    for i in range(nb):
        t = i * beat
        if t > dur - 0.2 or t < intro - 0.01: continue
        p8 = i % 8     # 드럼은 절반 속도: 8박(빠른 박) = 느긋한 한 마디
        if p8 in (0, 5) or (p8 == 3 and i % 16 == 11):
            add(dr, t, K, P['drums']); add(kenv, t, ke)
        if p8 == 4: add(dr, t, S, P['drums'] * 0.85); add(dr, t + 0.004, C, P['drums'])
        if p8 == 7 and i % 16 == 15: add(dr, t + 0.5 * beat, R, P['drums'])
        add(dr, t, Sh, P['drums'] * (1.0 if p8 % 2 == 0 else 0.7))          # 빠른 박마다 하이햇
        if P['hats16'] and (p8 in (2, 6) or rng.random() < 0.25):
            add(dr, t + sw * beat, Sh, P['drums'] * 0.5)                      # 사이사이 잘게
    # 멜로디: 플럭과 오르골, 빠른 박의 8분 위에서 통통
    phrase = None
    for b in range(nbars):
        t0 = b * bar
        if t0 < intro or t0 > dur - bar * 0.5: continue
        root, iv = CH[prog[(b // 2) % 4]]; root += KEY
        if b % 4 in (0, 2) or phrase is None:
            grid = list(np.arange(0, 4, 0.5))
            slots = sorted(s_ for s_ in grid if rng.random() < P['mel']) or [0.0, 1.0]
            pitches = []; cur = 2
            for _ in slots:
                cur = int(np.clip(cur + rng.choice([-1, 1, 1, 2, -2, 0]), 0, 7))
                pitches.append(72 + KEY + [0, 2, 4, 7, 9, 12, 14, 16][cur])
            phrase = list(zip(slots, pitches))
        else:
            phrase = [(s_, p_) for s_, p_ in phrase[:-1]] + [(phrase[-1][0], 72 + (root + iv[2]) % 12 + 12)]
        inst = pluck if (b // 4) % 2 == 0 else musicbox
        for s_, p_ in phrase:
            off = (sw - .5) * beat if (s_ % 1) else 0
            tn = t0 + s_ * beat + off
            if any(-0.25 < tn - a < 0.45 for a in avoid): continue   # 효과음 자리는 비워 둠
            add(mel, t0 + s_ * beat + off, inst(p_, 0.85 + rng.uniform(-.1, .1)), P['box'] * (1.0 if inst is pluck else 0.8))
    # 레코드 잡음
    idx = rng.integers(0, n, int(dur * 40)); cr = np.zeros(n); cr[idx] = rng.uniform(-1, 1, len(idx))
    vin = lp(cr, 3000) * 0.25 + lp(rng.standard_normal(n), 700) * 0.006
    # 섞기: 킥에 맞춰 살짝 숨쉬기(사이드체인), 전체를 먹먹하게(기준 곡처럼 고음 거의 없음), 테이프 질감
    pump = 1 - 0.12 * np.clip(lp(kenv, 30, 1), 0, 1)
    mix = (keys * 1.5 + mel * 1.7) * pump + bs * 0.55 * pump + dr * 0.8 + vin * 0.6
    mix = lp(mix, 6500, 2)
    mix = np.tanh(mix * 1.3) / np.tanh(1.3)
    mix = mix[:int(dur * SR)]
    fo = int(min(1.2, dur * 0.06) * SR); mix[-fo:] *= np.linspace(1, 0, fo)
    fi = int(0.15 * SR); mix[:fi] *= np.linspace(0, 1, fi)
    mix /= np.sqrt(np.mean(mix ** 2)) + 1e-9
    return mix * 10 ** (-16 / 20)   # 배경음 RMS -16dBFS

# ---------------- 효과음 ----------------
def _sq(f, n, duty=.5): ph = (np.arange(n) * f / SR) % 1; return np.where(ph < duty, 1., -1.)
def _env(n, k): return np.exp(-np.arange(n) / SR * k)
def sfx_sig(kind, v, rng, key=0):
    P5 = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21]   # 장조 펜타토닉 계단
    if kind == 'drop':   n = int(.45 * SR); return _whoosh(n, False, rng) * .5
    if kind == 'land':   n = int(.3 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(90 + 210 * np.exp(-t * 14)) / SR) * _env(n, 9) * 1.0
    if kind == 'pop':    n = int(.07 * SR); return lp(_sq(hz(76 + key + [0, 3, 5, 8][(v or 0) % 4] - 0), n), 4000) * _env(n, 40) * .35
    if kind == 'sparkle':
        out = np.zeros(int(.6 * SR))
        for k, m in enumerate((84, 88, 91, 96)): add(out, k * .06, _ding(m + key, .35), .5)
        return out
    if kind in ('whoosh_out', 'whoosh_in', 'swipe'): n = int((.35 if kind != 'swipe' else .25) * SR); return _whoosh(n, kind != 'whoosh_in', rng) * .8
    if kind == 'thud':   return _thunk(115, rng) * .7
    if kind == 'jump':   n = int(.2 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(380 + 380 * (1 - np.exp(-t * 15))) / SR) * _env(n, 12) * .45
    if kind == 'stamp':
        out = np.zeros(int(.3 * SR)); add(out, 0, _thunk(165, rng), 1.0); add(out, 0, _ding(88 + key, .3), .15); return out
    if kind == 'stamp_big':
        n = int(.3 * SR); b = lp(_sq(hz(40), n), 400) * _env(n, 12) * .35
        th = _thunk(90, rng); b[:len(th)] += th * 1.2; return b
    if kind == 'tick':   n = int(.06 * SR); return lp(_sq(hz(72 + key + P5[min(v or 0, 9)]), n), 3500) * _env(n, 35) * .5
    if kind == 'alert':
        out = np.zeros(int(.3 * SR)); n = int(.09 * SR)
        add(out, 0, lp(_sq(hz(88 + key), n), 4000) * _env(n, 20), .5); add(out, .12, lp(_sq(hz(84 + key), int(.12 * SR)), 4000) * _env(int(.12 * SR), 15), .5); return out
    if kind == 'check':  return _ding(72 + key + P5[min((v or 0) + 3, 9)], .3) * .55
    if kind == 'riser':  n = int(.95 * SR); return _whoosh(n, True, rng) * .7
    if kind == 'chime':  return _ding(91 + key, .5) * .45 + np.concatenate([np.zeros(int(.08 * SR)), _ding(96 + key, .42)]) [:int(.5 * SR)] * .3
    if kind == 'type':   n = int(.03 * SR); return lp(hp(rng.standard_normal(n), 2000), 6000) * _env(n, 120) * .3
    raise ValueError('모르는 효과음: ' + kind)
def _ding(m, l):
    n = int(l * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * hz(m) * t) + .3 * _sq(hz(m), n) * .5) * np.exp(-t * 7) * np.minimum(1, t * 500)
def _thunk(f, rng):
    n = int(.18 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * _env(n, 25) + lp(rng.standard_normal(n), 2500) * _env(n, 40) * .5
def _whoosh(n, up, rng):
    x = rng.standard_normal(n); out = np.zeros(n); k = 16; seg = n // k
    for i in range(k):
        fc = 600 + (i / (k - 1) if up else 1 - i / (k - 1)) * 5000
        out[i * seg:(i + 1) * seg] = lp(x, fc)[i * seg:(i + 1) * seg]
    return out * np.sin(np.pi * np.arange(n) / n) * .6

def make_sfx(dur, events, seed, key=0):
    rng = np.random.default_rng(seed + 1); out = np.zeros(int(dur * SR))
    for e in events:
        t, kind = float(e[0]), e[1]; v = e[2] if len(e) > 2 else None
        add(out, t, sfx_sig(kind, v, rng, key))
    return out * 0.5

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dur', type=float, required=True); ap.add_argument('--mood', default='bright', choices=list(MOODS))
    ap.add_argument('--seed', default='tenbylabs'); ap.add_argument('--events'); ap.add_argument('--out', default='out/audio.wav')
    ap.add_argument('--music-only', action='store_true'); ap.add_argument('--sfx-only', action='store_true')
    a = ap.parse_args()
    seed = int(hashlib.sha256(a.seed.encode()).hexdigest()[:8], 16)
    N = int(a.dur * SR)
    events = json.load(open(a.events)) if a.events else []
    avoid = [float(e[0]) for e in events if e[1] in TONAL]
    music = np.zeros(N) if a.sfx_only else make_music(a.dur, a.mood, seed, avoid)
    sfx = np.zeros(N) if a.music_only else make_sfx(a.dur, events, seed, key_of(a.mood))
    env = lp(np.abs(sfx), 12, 1); env = env / (env.max() + 1e-9)
    duck = 1 - 0.55 * np.clip(env * 4, 0, 1)          # 효과음이 날 때만 배경음을 살짝 낮춤
    mix = music * duck + sfx
    pk = np.max(np.abs(mix)) + 1e-9
    if pk > 0.95: mix *= 0.95 / pk
    st = np.stack([mix, np.roll(mix, int(.006 * SR)) * .9 + mix * .1], 1)
    wavfile.write(a.out, SR, (np.clip(st, -1, 1) * 32767).astype(np.int16))
    print(f"{a.out}: {a.dur:.1f}초, 분위기 {a.mood}, 효과음 {len(events)}개")

if __name__ == '__main__':
    main()
