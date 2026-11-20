"""TENBY LABS 릴스 → HyperFrames 프로젝트.

python3 build.py 문구.json   →  project/index.html (HyperFrames 구성)
그다음 npm run render       →  out/reel.mp4 (1080x1920, 30fps, 음악 없음)

문구 파일 형식, 화면 디자인, 장면 시간표는 templates/reel-long 과 같다.
reel-long/gen.py 가 그린 화면(setT(t) 로 어느 순간이든 그릴 수 있는 페이지)을
GSAP 타임라인 하나에 묶어 HyperFrames 가 프레임 단위로 찍게 한다.
"""
import sys, os, re, json, shutil, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LONG = os.path.join(HERE, "..", "reel-long")
PROJ = os.path.join(HERE, "project")
MIN_SEC = 45

src = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(LONG, "example.json"))
allow_short = "--allow-short" in sys.argv  # 미리보기용. 초안에는 쓰지 않는다.

# 1. reel-long 의 화면을 만든다 (gen.py 는 고치지 않는다)
subprocess.run([sys.executable, os.path.join(LONG, "gen.py"), src], check=True)
page_path = os.path.join(LONG, "page.html")
page = open(page_path, encoding="utf-8").read()
os.remove(page_path)  # templates 폴더에 남기지 않는다

css = page[page.index("<style>") + 7: page.index("</style>")]
css = re.sub(r'url\("file://[^"]*/fonts/', 'url("fonts/', css)
body = page[page.index("<body>") + 6: page.index("<script>")]
script = page[page.index("<script>") + 8: page.rindex("</script>")]

# 2. 전체 길이(TOTAL)를 페이지에서 읽는다
probe = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8")
probe.write("<!doctype html><meta charset=utf-8><body>" + body + "<script>" + script +
            "\n;document.body.setAttribute('data-total', String(TOTAL));</script>")
probe.close()
chrome = os.environ.get("CHROME_PATH") or shutil.which("google-chrome") or shutil.which("chromium")
dom = subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--dump-dom", "file://" + probe.name],
                     capture_output=True, text=True, timeout=120).stdout
os.remove(probe.name)
m = re.search(r'data-total="([\d.]+)"', dom)
if not m:
    raise SystemExit("전체 길이를 읽지 못했습니다 (Chrome 확인)")
total = round(float(m.group(1)), 3)
print("전체 길이", total, "초")
if total < MIN_SEC and not allow_short:
    raise SystemExit(f"전체 {total}초: 45초보다 짧습니다. 시간을 늘리지 말고 항목이나 줄(내용)을 더 채우세요.")

# 3. HyperFrames 프로젝트를 쓴다
shutil.rmtree(PROJ, ignore_errors=True)
os.makedirs(os.path.join(PROJ, "fonts"))
for f in os.listdir(os.path.join(LONG, "fonts")):
    shutil.copy(os.path.join(LONG, "fonts", f), os.path.join(PROJ, "fonts", f))
shutil.copy(os.path.join(HERE, "node_modules", "gsap", "dist", "gsap.min.js"), PROJ)
shutil.copy(os.path.join(HERE, "hyperframes.json"), PROJ)

html = f"""<!doctype html>
<html lang="ko" data-resolution="portrait">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1080, height=1920">
<script src="gsap.min.js"></script>
<style>
{css}
#root{{position:absolute;inset:0}}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920" data-fps="30">
{body}
</div>
<script>
{script}
</script>
<script>
// HyperFrames 가 이 타임라인을 프레임마다 멈춰 놓고(seek) 찍는다. 그 순간을 setT 로 그린다.
(function () {{
  const tl = gsap.timeline({{ paused: true }});
  const clock = {{ t: 0 }};
  tl.to(clock, {{ t: {total}, duration: {total}, ease: "none", onUpdate: () => setT(clock.t) }}, 0);
  setT(0);
  window.__timelines = window.__timelines || {{}};
  window.__timelines["main"] = tl;
  tl.seek(0);
}})();
</script>
</body>
</html>
"""
open(os.path.join(PROJ, "index.html"), "w", encoding="utf-8").write(html)
json.dump({"total": total, "source": os.path.basename(src)}, open(os.path.join(PROJ, "meta.json"), "w"), ensure_ascii=False)
print("project/index.html 준비됨")
