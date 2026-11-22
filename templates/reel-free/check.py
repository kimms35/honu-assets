"""렌더한 릴스 점검.

python3 check.py out/reel.mp4

1. 길이 45초 이상, 1080x1920, 30fps 인지 본다.
2. 1초마다 한 장씩 프레임을 뽑아 out/check_1.png, check_2.png … (한 장에 8칸, 칸마다 시각 표시)로 묶는다.
   이 그림들을 Read 로 전부 직접 열어, 글자가 화면 밖으로 나가거나 잘리거나 겹친 곳, 슬라임이 가려진 곳,
   자막이 위쪽이 아닌 곳, 깨진 글꼴이 없는지 눈으로 확인한다.
3. 거의 검은 화면, 3초 넘게 화면이 그대로인 구간(시간 끌기)을 찾아 알려 준다.
문제가 있으면 마지막 줄이 "점검 실패"로 끝난다. 하나라도 있으면 고쳐서 다시 렌더한다.
"""
import sys, os, json, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageStat

src = sys.argv[1] if len(sys.argv) > 1 else "out/reel.mp4"
outdir = os.path.dirname(os.path.abspath(src))
HERE = os.path.dirname(os.path.abspath(__file__))

info = json.loads(subprocess.run(
    ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate:format=duration",
     "-of", "json", src], capture_output=True, text=True, check=True).stdout)
st = info["streams"][0]
dur = float(info["format"]["duration"])
num, den = st["r_frame_rate"].split("/")
fps = float(num) / float(den)
problems = []
if dur < 45: problems.append(f"길이 {dur:.1f}초: 45초 미만")
if (st["width"], st["height"]) != (1080, 1920): problems.append(f"크기 {st['width']}x{st['height']}: 1080x1920 아님")
if abs(fps - 30) > 0.01: problems.append(f"fps {fps}: 30 아님")
print(f"길이 {dur:.1f}초, {st['width']}x{st['height']}, {fps:g}fps")

tmp = tempfile.mkdtemp()
subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf", "fps=1,scale=270:-1", os.path.join(tmp, "f%03d.png")], check=True)
frames = sorted(os.listdir(tmp))
imgs = [Image.open(os.path.join(tmp, f)).convert("RGB") for f in frames]

font = ImageFont.truetype(os.path.join(HERE, "..", "reel-long", "fonts", "Pretendard-Bold.ttf"), 22)
per = 8
for k in range(0, len(imgs), per):
    chunk = imgs[k:k + per]
    w, h = chunk[0].size
    sheet = Image.new("RGB", (w * 4 + 50, (h + 34) * 2 + 20), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    for j, im in enumerate(chunk):
        x, y = 10 + (j % 4) * (w + 10), 10 + (j // 4) * (h + 34)
        sheet.paste(im, (x, y + 30))
        d.text((x, y + 2), f"{k + j}초", font=font, fill=(255, 220, 80))
    sheet.save(os.path.join(outdir, f"check_{k // per + 1}.png"))
print("프레임 묶음:", ", ".join(f"check_{i + 1}.png" for i in range((len(imgs) + per - 1) // per)), "(전부 열어서 확인)")

still = 0
for i, im in enumerate(imgs):
    if ImageStat.Stat(im.convert("L")).mean[0] < 6:
        problems.append(f"{i}초: 거의 검은 화면")
    if i > 0:
        diff = ImageStat.Stat(ImageChops.difference(im, imgs[i - 1]).convert("L")).mean[0]
        still = still + 1 if diff < 0.6 else 0
        if still == 3:
            problems.append(f"{i - 3}~{i}초: 3초 넘게 화면이 거의 그대로(시간 끌기)")

for p in problems: print("문제:", p)
print("점검 실패" if problems else "자동 점검 통과 (프레임 묶음 눈 확인은 따로 할 것)")
