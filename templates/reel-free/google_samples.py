"""Google Cloud 음성 합성(TTS) 한국어 목소리 견본 만들기.

쓰는 법 (Default 환경 클라우드 세션에서, 저장소 루트):
  python3 templates/reel-free/google_samples.py

- API 키는 환경의 네트워크 시크릿이 texttospeech.googleapis.com 요청에 자동으로 붙인다.
  이 스크립트는 키를 읽거나 적거나 출력하지 않는다.
- ko-KR 목소리 목록을 받아 drafts/tts-samples/google/voices.json 에 적고,
  남자 목소리를 위주로 최대 8개 견본(wav)을 같은 폴더에 만든다.
"""
import base64, json, os, sys, urllib.request, urllib.error

API = "https://texttospeech.googleapis.com/v1"
OUT = "drafts/tts-samples/google"
TEXT = "117만 토큰을 천 토큰으로 줄인 MCP가 있어요. 오늘은 이걸 클로드 코드에 붙이는 법을 볼게요."


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read()).get("error", {})
        except Exception:
            err = {}
        return e.code, {"error": {"status": err.get("status"), "message": (err.get("message") or "")[:200]}}


def rank(v):
    n = v["name"]
    tier = 0 if "Chirp3-HD" in n else 1 if "Chirp" in n else 2 if "Neural2" in n else 3 if "Wavenet" in n else 4
    return (0 if v.get("ssmlGender") == "MALE" else 1, tier, n)


def main():
    os.makedirs(OUT, exist_ok=True)
    code, res = call("GET", "/voices?languageCode=ko-KR")
    if code != 200:
        print("목소리 목록 실패:", code, res.get("error")); sys.exit(1)
    voices = [v for v in res.get("voices", []) if "ko-KR" in v.get("languageCodes", [])]
    voices.sort(key=rank)
    json.dump([{"name": v["name"], "gender": v.get("ssmlGender")} for v in voices],
              open(f"{OUT}/voices.json", "w"), ensure_ascii=False, indent=1)
    print("ko-KR 목소리", len(voices), "개")
    made = []
    for v in voices[:8]:
        code, r = call("POST", "/text:synthesize", {
            "input": {"text": TEXT},
            "voice": {"languageCode": "ko-KR", "name": v["name"]},
            "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 44100}})
        if code != 200:
            print(v["name"], "실패:", code, r.get("error"))
            if code in (401, 403):
                break
            continue
        open(f"{OUT}/{v['name']}.wav", "wb").write(base64.b64decode(r["audioContent"]))
        made.append(v["name"]); print(v["name"], v.get("ssmlGender"), "완료")
    print("견본", len(made), "개:", ", ".join(made))


if __name__ == "__main__":
    main()
