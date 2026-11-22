"""reel-free 작업 폴더 준비.

python3 kit.py            → project/ 를 새로 만든다 (글꼴, gsap, hyperframes.json, 슬라임 표정 15장)
python3 kit.py --example  → 위와 같고, example/index.html 을 project/index.html 로 복사해 둔다(구조 참고용)

project/slime/<표정>.png 는 256x224 픽셀 그림이다. 화면에서는 image-rendering:pixelated 로 키워 쓴다.
슬라임 그림 자체는 ../reel/make_reel.py 에서만 가져온다. 다른 곳에서 새로 그리지 않는다.
"""
import os, sys, shutil, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "reel"))
import make_reel as M
from PIL import Image

PROJ = os.path.join(HERE, "project")
shutil.rmtree(PROJ, ignore_errors=True)
os.makedirs(os.path.join(PROJ, "fonts"))
os.makedirs(os.path.join(PROJ, "slime"))

for f in os.listdir(os.path.join(HERE, "..", "reel-long", "fonts")):
    shutil.copy(os.path.join(HERE, "..", "reel-long", "fonts", f), os.path.join(PROJ, "fonts", f))
gsap = os.path.join(HERE, "node_modules", "gsap", "dist", "gsap.min.js")
if not os.path.exists(gsap):
    raise SystemExit("먼저 npm ci 를 실행하세요 (gsap 이 없습니다)")
shutil.copy(gsap, PROJ)
shutil.copy(os.path.join(HERE, "..", "reel-hf", "hyperframes.json"), PROJ)

for m in M.MOODS:
    M.slime_sprite(False, m).resize((256, 224), Image.NEAREST).save(os.path.join(PROJ, "slime", m + ".png"))

if "--example" in sys.argv:
    shutil.copy(os.path.join(HERE, "example", "index.html"), os.path.join(PROJ, "index.html"))

print("project/ 준비됨. 표정:", ", ".join(M.MOODS))
