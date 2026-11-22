"""TENBY LABS 릴스 배경음 + 효과음 생성기 (코드로 직접 만들어 저작권 걱정 없음).

기준 분위기: 채널 주인이 고른 큐트 카와이 로파이(Heart Bubbles 등) —
  80~94BPM, 장조, 아주 따뜻하고 먹먹한 소리(고음 거의 없음), 부드러운 피아노·오르골, 둥근 베이스, 작은 드럼, 레코드 잡음.
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
    return lp(hp(rng.standard_normal(n), 4000), 7000) * np.sin(np.pi * np.minimum(t / 0.07, 1)) * 0.08

# ---------------- 분위기별 설정 (진행은 흔한 재즈·로파이 화성 문법으로 직접 짠 것) ----------------
CH = {  # 근음(미디)과 구성음(근음 기준 반음)
    'Cmaj9': (48, [0, 4, 7, 11, 14]), 'Am9': (45, [0, 3, 7, 10, 14]), 'Dm9': (50, [0, 3, 7, 10, 14]),
    'G6': (43, [0, 4, 7, 9, 14]), 'Fmaj9': (41, [0, 4, 7, 11, 14]), 'Em7': (40, [0, 3, 7, 10, 14]),
    'G13sus': (43, [0, 5, 7, 10, 16]), 'E7b9': (40, [0, 4, 7, 10, 13]), 'Fm6': (41, [0, 3, 7, 9, 14]),
    'Bbmaj7': (46, [0, 4, 7, 11, 14]), 'D9': (50, [0, 4, 7, 10, 14]),
}
MOODS = {
    'calm':    dict(bpm=80, progs=[['Fmaj9', 'Em7', 'Dm9', 'Cmaj9'], ['Fmaj9', 'Fm6', 'Em7', 'Am9']], mel=0.35, drums=0.75, box=0.8),
    'bright':  dict(bpm=86, progs=[['Cmaj9', 'Am9', 'Dm9', 'G13sus'], ['Fmaj9', 'G6', 'Em7', 'Am9']], mel=0.55, drums=1.0, box=1.0),
    'playful': dict(bpm=92, progs=[['Fmaj9', 'G6', 'Em7', 'Am9'], ['Cmaj9', 'D9', 'Fmaj9', 'G13sus']], mel=0.75, drums=1.1, box=1.2),
    'focus':   dict(bpm=84, progs=[['Am9', 'Fmaj9', 'Cmaj9', 'G6'], ['Dm9', 'G13sus', 'Cmaj9', 'E7b9']], mel=0.4, drums=0.9, box=0.7),
}
PENTA = [0, 2, 4, 7, 9]  # C장조 펜타토닉

def make_music(dur, mood, seed):
    P = MOODS[mood]; rng = np.random.default_rng(seed)
    beat = 60 / P['bpm']; bar = 4 * beat; sw = 0.58  # 스윙(16분 뒷박을 조금 늦게)
    n = int((dur + 2) * SR)
    keys, bs, dr, mel, vin = (np.zeros(n) for _ in range(5))
    prog = P['progs'][rng.integers(len(P['progs']))]
    nbars = int(np.ceil(dur / bar)) + 1
    intro = min(3.2, dur * 0.1)                 # 훅 구간: 피아노만 가볍게
    for b in range(nbars):
        t0 = b * bar; root, iv = CH[prog[b % 4]]
        voic = [root + 12 + i for i in iv[1:]]  # 근음 빼고 가운데 음역으로
        while min(voic) < 55: voic = [v + 12 for v in voic]
        while max(voic) > 76: voic = [v - 12 for v in voic]
        for k, m in enumerate(sorted(voic)):    # 1박에 살짝 굴려 치기
            add(keys, t0 + k * 0.018 + rng.uniform(0, 0.006), piano(m, bar * 0.55, 0.7 + rng.uniform(-.08, .05), rng))
        for k, m in enumerate(sorted(voic)[1:]):  # 2박 반에 가볍게 다시
            add(keys, t0 + 1.5 * beat + (sw - .5) * beat + k * 0.012, piano(m, beat, 0.42, rng))
        if t0 >= intro - 0.01:
            add(bs, t0, bass(root, beat * 1.6)); add(bs, t0 + 2.5 * beat, bass(root + (7 if b % 2 else 12), beat * 0.9))
    # 드럼: 붐뱁 (킥 1, 2&a, 3& / 스네어 2·4 / 셰이커 8분 스윙)
    K, S, R, Sh = kick(rng), snare(rng), rim(rng), shaker(rng)
    kenv = np.zeros(n)
    nb = int(dur / beat) + 2
    for i in range(nb):
        t = i * beat
        if t < intro - 0.01 or t > dur - 0.2: continue
        p = i % 4
        if p == 0 or (p == 1 and i % 8 == 5): add(dr, t + (0.75 * beat if p == 1 else 0), K, P['drums']); add(kenv, t + (0.75 * beat if p == 1 else 0), np.exp(-np.arange(int(.3 * SR)) / SR * 9))
        if p == 2: add(dr, t + 0.5 * beat, K, P['drums'] * 0.8); add(kenv, t + 0.5 * beat, np.exp(-np.arange(int(.3 * SR)) / SR * 9))
        if p in (1, 3): add(dr, t, S, P['drums'] * 0.9)
        if p == 3 and i % 8 == 7: add(dr, t + 0.75 * beat, R, P['drums'])
        add(dr, t, Sh, P['drums']); add(dr, t + sw * beat, Sh, P['drums'] * 0.7)
    # 오르골 멜로디: 2마디 부르고 2마디 답하기, 쉼 많이. 화음 구성음에 맞춘 펜타토닉
    phrase = None
    for b in range(nbars):
        t0 = b * bar
        if t0 < intro or t0 > dur - bar * 0.6: continue
        root, iv = CH[prog[b % 4]]
        if b % 4 in (0, 2) or phrase is None:
            slots = [s for s in np.arange(0, 4, 0.5) if rng.random() < P['mel']] or [0.0]
            pitches = [72 + PENTA[rng.integers(5)] + (12 if rng.random() < 0.25 else 0) for _ in slots]
            phrase = list(zip(slots, pitches))
        else:  # 답하는 마디: 같은 리듬, 끝음만 화음 쪽으로
            phrase = [(s, p) for s, p in phrase[:-1]] + [(phrase[-1][0], 72 + (root + iv[2]) % 12)]
        for s, p in phrase:
            sw_off = (sw - 0.5) * beat if (s % 1) == 0.5 else 0
            add(mel, t0 + s * beat + sw_off, musicbox(p, 0.8 + rng.uniform(-.1, .1)), P['box'])
    # 레코드 잡음
    idx = rng.integers(0, n, int(dur * 40)); cr = np.zeros(n); cr[idx] = rng.uniform(-1, 1, len(idx))
    vin = lp(cr, 3000) * 0.25 + lp(rng.standard_normal(n), 700) * 0.006
    # 섞기: 킥에 맞춰 살짝 숨쉬기(사이드체인), 전체를 먹먹하게(기준 곡처럼 고음 거의 없음), 테이프 질감
    pump = 1 - 0.22 * np.clip(lp(kenv, 30, 1), 0, 1)
    mix = (keys * 1.0 + mel * 1.0) * pump + bs * 1.0 * pump + dr * 0.55 + vin
    mix = lp(mix, 4200, 2)
    mix = np.tanh(mix * 1.3) / np.tanh(1.3)
    mix = mix[:int(dur * SR)]
    fo = int(min(1.2, dur * 0.06) * SR); mix[-fo:] *= np.linspace(1, 0, fo)
    fi = int(0.15 * SR); mix[:fi] *= np.linspace(0, 1, fi)
    mix /= np.sqrt(np.mean(mix ** 2)) + 1e-9
    return mix * 10 ** (-16 / 20)   # 배경음 RMS -16dBFS

# ---------------- 효과음 ----------------
def _sq(f, n, duty=.5): ph = (np.arange(n) * f / SR) % 1; return np.where(ph < duty, 1., -1.)
def _env(n, k): return np.exp(-np.arange(n) / SR * k)
def sfx_sig(kind, v, rng):
    if kind == 'drop':   n = int(.45 * SR); return _whoosh(n, False, rng) * .5
    if kind == 'land':   n = int(.3 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(90 + 210 * np.exp(-t * 14)) / SR) * _env(n, 9) * 1.0
    if kind == 'pop':    n = int(.07 * SR); return lp(_sq(hz(76 + 3 * (v or 0)), n), 4000) * _env(n, 40) * .35
    if kind == 'sparkle':
        out = np.zeros(int(.6 * SR))
        for k, m in enumerate((84, 88, 91, 96)): add(out, k * .06, _ding(m, .35), .5)
        return out
    if kind in ('whoosh_out', 'whoosh_in', 'swipe'): n = int((.35 if kind != 'swipe' else .25) * SR); return _whoosh(n, kind != 'whoosh_in', rng) * .8
    if kind == 'thud':   return _thunk(115, rng) * .7
    if kind == 'jump':   n = int(.2 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(380 + 380 * (1 - np.exp(-t * 15))) / SR) * _env(n, 12) * .45
    if kind == 'stamp':
        out = np.zeros(int(.3 * SR)); add(out, 0, _thunk(165, rng), 1.0); add(out, 0, _ding(88, .3), .15); return out
    if kind == 'stamp_big':
        n = int(.3 * SR); b = lp(_sq(hz(40), n), 400) * _env(n, 12) * .35
        th = _thunk(90, rng); b[:len(th)] += th * 1.2; return b
    if kind == 'tick':   n = int(.06 * SR); return lp(_sq(hz(72 + 2 * (v or 0)), n), 3500) * _env(n, 35) * .5
    if kind == 'alert':
        out = np.zeros(int(.3 * SR)); n = int(.09 * SR)
        add(out, 0, lp(_sq(hz(88), n), 4000) * _env(n, 20), .5); add(out, .12, lp(_sq(hz(84), int(.12 * SR)), 4000) * _env(int(.12 * SR), 15), .5); return out
    if kind == 'check':  return _ding(79 + [0, 2, 4, 7, 9, 12][min(v or 0, 5)], .3) * .55
    if kind == 'riser':  n = int(.95 * SR); return _whoosh(n, True, rng) * .7
    if kind == 'chime':  return _ding(91, .5) * .45 + np.concatenate([np.zeros(int(.08 * SR)), _ding(96, .42)]) [:int(.5 * SR)] * .3
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

def make_sfx(dur, events, seed):
    rng = np.random.default_rng(seed + 1); out = np.zeros(int(dur * SR))
    for e in events:
        t, kind = float(e[0]), e[1]; v = e[2] if len(e) > 2 else None
        add(out, t, sfx_sig(kind, v, rng))
    return out * 0.5

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dur', type=float, required=True); ap.add_argument('--mood', default='bright', choices=list(MOODS))
    ap.add_argument('--seed', default='tenbylabs'); ap.add_argument('--events'); ap.add_argument('--out', default='out/audio.wav')
    ap.add_argument('--music-only', action='store_true'); ap.add_argument('--sfx-only', action='store_true')
    a = ap.parse_args()
    seed = int(hashlib.sha256(a.seed.encode()).hexdigest()[:8], 16)
    N = int(a.dur * SR)
    music = np.zeros(N) if a.sfx_only else make_music(a.dur, a.mood, seed)
    events = json.load(open(a.events)) if a.events else []
    sfx = np.zeros(N) if a.music_only else make_sfx(a.dur, events, seed)
    env = lp(np.abs(sfx), 12, 1); env = env / (env.max() + 1e-9)
    duck = 1 - 0.45 * np.clip(env * 4, 0, 1)          # 효과음이 날 때만 배경음을 살짝 낮춤
    mix = music * duck + sfx
    pk = np.max(np.abs(mix)) + 1e-9
    if pk > 0.95: mix *= 0.95 / pk
    st = np.stack([mix, np.roll(mix, int(.006 * SR)) * .9 + mix * .1], 1)
    wavfile.write(a.out, SR, (np.clip(st, -1, 1) * 32767).astype(np.int16))
    print(f"{a.out}: {a.dur:.1f}초, 분위기 {a.mood}, 효과음 {len(events)}개")

if __name__ == '__main__':
    main()
