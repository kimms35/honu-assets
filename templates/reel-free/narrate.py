"""slimebot.ai 릴스 나레이션 입히기 (기본: 구글 TTS, 목소리 ko-KR-Chirp3-HD-Despina).

채널 주인 결정(2026-11-24): 배경음은 빼고, 효과음은 그대로, 나레이션을 넣는다.

쓰는 법 (Default 클라우드 환경의 Claude Code 루틴에서만 돈다. 키는 그 환경의 네트워크 시크릿으로
구글·타입캐스트 요청에 프록시가 자동으로 붙인다. 이 스크립트는 키를 읽거나 넣거나 출력하지 않는다):

  python3 templates/reel-free/narrate.py drafts/<날짜>-reel-<slug>

기본은 구글 TTS Despina(여성) 다 (채널 주인 확정 2026-11-24: 타입캐스트 무료 계정 차단 뒤 구글 목소리를 들어 보고
Algenib 와 비교해 Despina 로 확정).
구글 키는 같은 환경의 네트워크 시크릿이 texttospeech.googleapis.com 요청에 X-Goog-Api-Key 로 붙인다.
narration.json 의 voice 가 "ko-KR-" 로 시작하지 않으면(예: 예전 "필재") 구글에선 무시하고 Despina 를 쓴다.

  다른 구글 목소리:  ... --voice ko-KR-Chirp3-HD-Algenib
  타입캐스트로:      ... --engine typecast            (narration.json 의 voice, 없으면 "필재")
  문장 앞뒤 맥락(smart 감정)은 타입캐스트에서만 쓴다.

그 폴더에 있어야 하는 것: reel.mp4(영상, 지금 소리는 무엇이든 상관없음), events.json(효과음 시각), narration.json
narration.json 형식:
  {"voice": "ko-KR-Chirp3-HD-Despina", "tempo": 1.1,
   "lines": [{"start": 0.0, "end": 3.3, "text": "말할 문장"}, ...]}
  start/end 는 그 문장이 들어갈 장면의 시작·끝 초. 문장은 그 안에 들어가게 짧게 쓴다.

만드는 것: 같은 폴더의 reel_narrated.mp4 (영상 그대로 + 나레이션 + 효과음, 배경음 없음),
          narration_result.json (줄마다 실제 길이, 속도 조정 배율, 겹침 여부, 쓴 voice_id).
reel.mp4 는 건드리지 않는다. 바꿔 끼우는 건 부르는 쪽이 결과를 확인한 뒤에 한다.
"""
import argparse, base64, json, os, re, subprocess, sys, tempfile, urllib.request, urllib.error
import numpy as np
from scipy.io import wavfile

API = "https://api.typecast.ai"
GOOGLE_API = "https://texttospeech.googleapis.com"
SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
MAX_TEMPO = 1.3      # 장면에 안 들어가면 이 배율까지만 빠르게 한다
GAP = 0.12           # 문장 사이 최소 쉼(초)


def call(method, path, body=None, timeout=90, base=API):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(base + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read()


def find_voice(name):
    for path in ("/v3/voices?model=ssfm-v30", "/v2/voices?model=ssfm-v30", "/v3/voices", "/v2/voices"):
        try:
            _, _, raw = call("GET", path, timeout=30)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise SystemExit(f"타입캐스트 인증 실패({e.code}): 이 환경에 네트워크 시크릿이 붙지 않음")
            continue
        d = json.loads(raw)
        items = d if isinstance(d, list) else d.get("voices") or d.get("items") or d.get("data") or []
        for v in items:
            n = v.get("voice_name")
            names = [n] if isinstance(n, str) else list((n or {}).values())
            if any(name == x or name in str(x) for x in names):
                return v["voice_id"], v
    raise SystemExit(f"목소리 '{name}' 를 찾지 못함")


def tts(voice_id, text, prev_text, next_text, tempo):
    text, prev_text, next_text = speakable(text), speakable(prev_text), speakable(next_text)
    base = {"voice_id": voice_id, "text": text, "model": "ssfm-v30", "language": "kor",
            "output": {"audio_format": "wav", "audio_tempo": tempo, "volume": 100}}
    tries = [dict(base, prompt={"emotion_type": "smart", "previous_text": prev_text, "next_text": next_text}),
             dict(base, prompt={"emotion_preset": "normal"}), base]
    last = None
    for body in tries:
        try:
            st, ctype, raw = call("POST", "/v1/text-to-speech", body)
            if raw[:4] == b"RIFF":
                return raw
            last = f"오디오가 아닌 응답: {ctype} {raw[:120]!r}"
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read()[:200]!r}"
            if e.code in (401, 403):
                break
    raise SystemExit(f"음성 생성 실패: {last}")


def speakable(text):
    """음성으로 보낼 문장만 다듬는다(화면 자막은 그대로).
    채널 주인(2026-11-24): "2,500개를 '이 오백 개'로 읽는다. 숫자는 '이천오백 개'처럼 읽게."
    → 숫자 속 천 단위 쉼표를 뺀다(2,500 → 2500, 1,170,000 → 1170000)."""
    return re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", text)


def google_tts(voice, text, tempo):
    text = speakable(text)
    lang = "-".join(voice.split("-")[:2])
    audio = {"audioEncoding": "LINEAR16", "sampleRateHertz": SR}
    tries = [dict(audio, speakingRate=tempo), audio]   # 속도 지정을 못 받는 목소리면 기본 속도로 다시 한 번
    last = None
    for cfg in tries:
        body = {"input": {"text": text}, "voice": {"languageCode": lang, "name": voice}, "audioConfig": cfg}
        try:
            _, _, raw = call("POST", "/v1/text:synthesize", body, base=GOOGLE_API)
            return base64.b64decode(json.loads(raw)["audioContent"])
        except urllib.error.HTTPError as e:
            err = json.loads(e.read() or b"{}").get("error", {})
            last = f"HTTP {e.code} {err.get('status')}: {str(err.get('message'))[:200]}"
            if e.code != 400:
                break
    raise SystemExit(f"구글 음성 생성 실패: {last}")


def to_mono(path):
    sr, x = wavfile.read(path)
    x = x.astype(np.float32)
    if x.ndim > 1: x = x.mean(1)
    x /= 32768.0 if np.abs(x).max() > 2 else 1.0
    if sr != SR:
        x = np.interp(np.arange(int(len(x) * SR / sr)) * sr / SR, np.arange(len(x)), x)
    return x


def speedup(x, factor, tmp):
    a, b = os.path.join(tmp, "s_in.wav"), os.path.join(tmp, "s_out.wav")
    wavfile.write(a, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a, "-filter:a", f"atempo={factor:.3f}", b], check=True)
    return to_mono(b)


def trim_silence(x, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0: return x
    return x[max(0, idx[0] - int(0.02 * SR)): min(len(x), idx[-1] + int(0.06 * SR))]


GOOGLE_VOICE = "ko-KR-Chirp3-HD-Despina"


def main(folder, engine="google", voice=None):
    n = json.load(open(os.path.join(folder, "narration.json")))
    if voice: n["voice"] = voice
    if engine == "google" and not str(n.get("voice", "")).startswith("ko-KR-"):
        n["voice"] = GOOGLE_VOICE
    video = os.path.join(folder, "reel.mp4")
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", video]).decode().strip())
    voice_id = n["voice"] if engine == "google" else find_voice(n.get("voice", "필재"))[0]
    tempo = float(n.get("tempo", 1.1))
    lines = n["lines"]
    tmp = tempfile.mkdtemp()
    narr = np.zeros(int((dur + 2) * SR), np.float32)
    report, cursor = [], 0.0
    for i, ln in enumerate(lines):
        if engine == "google":
            raw = google_tts(voice_id, ln["text"], tempo)
        else:
            raw = tts(voice_id, ln["text"], lines[i - 1]["text"] if i else "", lines[i + 1]["text"] if i + 1 < len(lines) else "", tempo)
        p = os.path.join(tmp, f"l{i}.wav"); open(p, "wb").write(raw)
        x = trim_silence(to_mono(p))
        start = max(float(ln["start"]) + 0.08, cursor + GAP)
        slot = float(ln["end"]) - start - 0.05
        factor = 1.0
        if len(x) / SR > slot > 0.3:
            factor = min(MAX_TEMPO, (len(x) / SR) / slot)
            x = speedup(x, factor, tmp)
        s = int(start * SR); e = min(len(narr), s + len(x))
        narr[s:e] += x[:e - s]
        cursor = start + len(x) / SR
        report.append({"i": i, "start": round(start, 2), "len": round(len(x) / SR, 2), "speedup": round(factor, 2),
                       "overflow_sec": round(max(0.0, cursor - float(ln["end"])), 2)})
    narr = narr[:int(dur * SR)]
    rms = np.sqrt(np.mean(narr[np.abs(narr) > 0.01] ** 2)) + 1e-9
    narr *= 10 ** (-16 / 20) / rms                      # 나레이션 RMS 약 -16dBFS
    sfx_path = os.path.join(tmp, "sfx.wav")
    ev = os.path.join(folder, "events.json")
    cmd = [sys.executable, os.path.join(HERE, "music.py"), "--dur", f"{dur:.2f}", "--sfx-only", "--out", sfx_path]
    if os.path.exists(ev): cmd += ["--events", ev]
    subprocess.run(cmd, check=True)
    sfx = to_mono(sfx_path)[:len(narr)]
    sfx = np.pad(sfx, (0, len(narr) - len(sfx)))
    env = np.convolve(np.abs(narr), np.ones(int(0.15 * SR)) / int(0.15 * SR), "same")
    env = np.clip(env / (env.max() + 1e-9) * 4, 0, 1)
    mix = narr + sfx * 0.55 * (1 - 0.4 * env)           # 말할 때 효과음을 조금 낮춤
    pk = np.abs(mix).max() + 1e-9
    if pk > 0.95: mix *= 0.95 / pk
    out_wav = os.path.join(tmp, "mix.wav")
    wavfile.write(out_wav, SR, (np.stack([mix, mix], 1) * 32767).astype(np.int16))
    out = os.path.join(folder, "reel_narrated.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", out_wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    res = {"engine": engine, "voice_id": voice_id, "voice": n.get("voice", "필재"), "tempo": tempo, "duration": round(dur, 2),
           "lines": report, "max_overflow_sec": max([r["overflow_sec"] for r in report] or [0]),
           "chars": sum(len(l["text"]) for l in lines)}
    json.dump(res, open(os.path.join(folder, "narration_result.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--engine", choices=["google", "typecast"], default="google")
    ap.add_argument("--voice", help="narration.json 의 voice 대신 쓸 목소리 (구글 기본 ko-KR-Chirp3-HD-Despina)")
    a = ap.parse_args()
    main(a.folder, a.engine, a.voice)
