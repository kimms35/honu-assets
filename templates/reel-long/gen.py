"""TENBY LABS 긴 릴스 틀 (45초 이상): 훅 → 항목 3~4개 → 정리.
python3 gen.py 문구.json  →  같은 폴더에 page.html 을 만든다. 영상은 render.js 로 찍는다.
항목 종류: "chat"(흔한 질문 → 고친 질문), "list"(순서·체크리스트·바뀐 점을 한 줄씩).
"""
import sys, os, io, json, base64
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "reel"))
import make_reel as M          # 슬라임 그림만 가져온다
from PIL import Image

src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "example.json")
C = json.load(open(src, encoding="utf-8"))
N = len(C["items"])
if not 3 <= N <= 4:
    raise SystemExit("항목은 3개나 4개여야 합니다")
F = "file://" + os.path.join(HERE, "fonts")
BRAND = "TENBY LABS"

def sprite(mood):
    im = M.slime_sprite(False, mood).resize((256, 224), Image.NEAREST)
    b = io.BytesIO(); im.save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
SPR = {m: sprite(m) for m in ("base", "glint", "surprise", "excited", "smile")}

CSS = f"""
@font-face{{font-family:P;font-weight:900;src:url("{F}/Pretendard-Black.ttf")}}
@font-face{{font-family:P;font-weight:800;src:url("{F}/Pretendard-ExtraBold.ttf")}}
@font-face{{font-family:P;font-weight:700;src:url("{F}/Pretendard-Bold.ttf")}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1920px;overflow:hidden;font-family:P;font-weight:700;color:#F4F2EC;position:relative;
 background:radial-gradient(60% 30% at 50% 70%,rgba(255,120,160,.24),transparent 70%),linear-gradient(#150C14,#1B1019 55%,#150C14)}}
body:before{{content:"";position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(255,255,255,.022) 0 2px,transparent 2px 6px);pointer-events:none}}
.brand{{position:absolute;left:60px;top:150px;font-size:32px;letter-spacing:3px;color:rgba(255,255,255,.6);font-weight:900}}
.scene{{position:absolute;inset:0;opacity:0;display:none}}
.tag{{position:absolute;left:50%;top:330px;background:#FFCE54;color:#1B1D36;border-radius:20px;padding:16px 34px;font-size:46px;font-weight:900;white-space:nowrap;box-shadow:0 10px 40px rgba(255,206,84,.35)}}
.hl{{position:absolute;left:0;right:0;text-align:center;font-size:126px;font-weight:900;letter-spacing:-4px;line-height:1}}
.hl em{{font-style:normal;color:#FF7B6B}} .cap em{{font-style:normal;color:#FFCE54}}
.card{{position:absolute;left:46px;right:46px;top:250px;border-radius:34px;background:linear-gradient(#21151F,#190F17);border:4px solid #FF8A3D;padding:22px;
 box-shadow:0 0 0 1px rgba(255,138,61,.25),0 0 46px rgba(255,138,61,.22),0 30px 80px rgba(0,0,0,.55)}}
.row{{border-radius:22px;border:2px solid #42303E;background:#2B1C28;display:flex;align-items:center}}
.head{{height:110px;padding:0 26px}}
.pg{{position:relative;height:76px;margin-right:22px;flex:none}}
.pg .ln{{position:absolute;left:12px;right:12px;top:56px;height:6px;background:#4A3646}}
.pg .fill{{position:absolute;left:12px;top:56px;height:6px;background:#FF8A3D;width:0}}
.pg i{{position:absolute;top:50px;width:18px;height:18px;background:#4A3646}} .pg i.done{{background:#FF8A3D}}
.pg img{{position:absolute;top:0;width:44px;image-rendering:pixelated}}
.ttl b{{display:block;font-size:40px;font-weight:800;color:#FFCE54}} .ttl span{{font-size:25px;color:#C9B6C4}}
.src{{margin-left:auto;text-align:right;font-size:23px;font-weight:800;color:#E4D8E0;max-width:300px}} .src span{{display:block;font-size:19px;color:#9C8A97}}
.how{{height:96px;margin-top:16px;padding:0 22px;font-size:38px;font-weight:800}}
.pill{{background:#FFCE54;color:#1B1D36;border-radius:12px;padding:8px 16px;font-size:28px;font-weight:900;margin-right:20px;flex:none}}
.pill.bad{{background:#6B4C63;color:#F4E8F0}}
.meter{{margin-left:auto;display:flex;align-items:center;gap:14px;font-size:24px;color:#C9B6C4;font-weight:800;flex:none}}
.meter .mb{{width:200px;height:20px;border-radius:10px;background:#4A3646;overflow:hidden}}
.meter .mb b{{display:block;height:100%;width:0;border-radius:10px;background:#E5484D}}
.win{{margin-top:16px;height:600px;border-radius:22px;background:#F6F3EC;color:#22233A;position:relative;overflow:hidden}}
.bar{{height:62px;border-bottom:2px solid #E2DED3;display:flex;align-items:center;padding:0 22px;font-size:24px;font-weight:800;gap:12px}}
.bar i{{width:22px;height:22px;border-radius:6px;background:#FF8A3D}}
.load{{position:absolute;left:0;top:60px;height:5px;width:0;background:#FF8A3D}}
.me{{position:absolute;right:24px;top:88px;max-width:760px;background:#E6E1D6;border-radius:22px;padding:20px 26px;font-size:33px;font-weight:800;line-height:1.42}}
.me mark{{background:transparent no-repeat;background-image:linear-gradient(#FFE08A,#FFE08A);background-size:0% 100%;color:inherit;border-radius:6px;padding:0 2px}}
.ai{{position:absolute;left:28px;right:28px;font-size:32px;line-height:1.5;font-weight:700}}
.ai p{{white-space:pre}} .ai .chk{{color:#1E9D5C;font-weight:900;margin-top:8px}}
.chkbar{{height:6px;border-radius:3px;background:#3FC47A;width:0;margin-top:6px}}
.dots{{position:absolute;left:34px;display:flex;gap:10px}} .dots i{{width:16px;height:16px;border-radius:9px;background:#B7B1A5}}
.stamp{{position:absolute;right:40px;border:5px solid #E5484D;color:#E5484D;font-size:40px;font-weight:900;padding:6px 20px;border-radius:12px;background:rgba(255,255,255,.7)}}
.inp{{position:absolute;left:18px;right:18px;bottom:18px;min-height:78px;border-radius:18px;border:2px solid #DDD8CC;background:#fff;display:flex;align-items:flex-start;padding:14px 16px;gap:16px;line-height:1.4}}
.inp i{{width:46px;height:46px;border-radius:12px;border:2px solid #DDD8CC;display:flex;align-items:center;justify-content:center;font-style:normal;color:#55545E;font-size:30px;flex:none}}
.inp .tx{{flex:1;min-width:0;white-space:normal;word-break:keep-all;color:#22233A;font-size:28px;font-weight:800}} .inp .ph{{color:#A29F95}}
.inp .cur{{display:inline-block;width:3px;height:30px;background:#FF8A3D;vertical-align:-5px;margin-left:2px}}
.inp .send{{width:50px;height:50px;border-radius:14px;background:#D9D3C7;flex:none;display:flex;align-items:center;justify-content:center;color:#fff;font-size:30px;font-weight:900}}
/* 목록형 */
.lst{{position:absolute;left:22px;right:22px;top:84px}}
.li{{display:flex;align-items:center;gap:20px;background:#fff;border:2px solid #E2DED3;border-radius:18px;padding:16px 20px;margin-bottom:14px}}
.li .k{{width:52px;height:52px;border-radius:14px;background:#2B1C28;color:#FFCE54;font-size:28px;font-weight:900;display:flex;align-items:center;justify-content:center;flex:none}}
.li b{{display:block;font-size:32px;font-weight:900;color:#22233A}} .li span{{display:block;font-size:25px;color:#6F6A61;margin-top:2px}}
.li .ok{{margin-left:auto;flex:none;width:44px;height:44px;border-radius:22px;background:#3FC47A;color:#fff;font-size:28px;font-weight:900;display:flex;align-items:center;justify-content:center}}
.li .lb{{height:5px;border-radius:3px;background:#FF8A3D;width:0;margin-top:8px}}
.chip{{position:absolute;right:34px;top:150px;height:92px;display:flex;flex-direction:column;justify-content:center;z-index:5;background:#2B1C28;color:#F4E8F0;border-radius:18px;padding:0 22px;font-size:22px;font-weight:800;text-align:right;border:3px solid #FF8A3D;box-shadow:0 10px 30px rgba(0,0,0,.4)}}
.chip b{{display:block;font-size:40px;color:#FFCE54;font-weight:900;line-height:1.1}}
.tags{{display:flex;justify-content:flex-end;gap:12px;margin-top:14px;font-size:20px;color:#E4D8E0}}
.tags span{{background:#2B1C28;border-radius:99px;padding:6px 16px}} .tags i{{display:inline-block;width:10px;height:10px;border-radius:9px;background:#3FC47A;margin-right:8px}}
.cap{{position:absolute;left:30px;right:30px;top:1238px;text-align:center;font-size:56px;font-weight:900;letter-spacing:-1px;line-height:1.25;text-shadow:0 4px 0 rgba(0,0,0,.5)}}
.shead{{display:flex;align-items:center;padding:14px 16px 22px;font-size:28px;color:#E4D8E0;font-weight:800;gap:14px}}
.shead i{{width:30px;height:30px;border-radius:8px;background:#FF8A3D}}
.shead span{{margin-left:auto;font-size:22px;border:2px solid #42303E;border-radius:99px;padding:6px 18px;background:#2B1C28}}
.segs{{display:flex;gap:10px;margin:0 16px 22px}} .segs i{{flex:1;height:14px;border-radius:4px;background:#4A3646;position:relative;overflow:hidden}}
.segs i b{{position:absolute;inset:0;background:#FFCE54;transform-origin:50% 100%;transform:scaleY(0)}}
.item{{margin-bottom:20px;padding:0 34px}}
.item u{{position:relative;width:64px;height:64px;border-radius:14px;border:4px solid #5A4256;background:#1F141D;margin-right:34px;flex:none;text-decoration:none;display:flex;align-items:center;justify-content:center}}
.item u b{{color:#fff;font-size:40px;font-weight:900;line-height:1}}
.item u em{{position:absolute;inset:-4px;border-radius:14px;border:4px solid #3FC47A;opacity:0}}
.item div b{{display:block;font-size:46px;font-weight:900}} .item div span{{font-size:29px;color:#C9B6C4}}
.item s{{margin-left:auto;text-decoration:none;font-size:22px;color:#3FC47A;border:2px solid #2C6E4B;border-radius:99px;padding:6px 14px;background:#143424}}
.foot{{text-align:center;color:#3FC47A;font-size:38px;font-weight:900;padding:6px 0 14px}}
#sl{{position:absolute;image-rendering:pixelated;transform-origin:50% 100%}}
#sh{{position:absolute;height:20px;border-radius:50%;background:rgba(0,0,0,.45);filter:blur(5px)}}
"""

GAP = 79 if N == 3 else 60
def head(i, it):
    dots = "".join(f'<i style="left:{12 + j * GAP}px"></i>' for j in range(N))
    w = 54 + GAP * (N - 1)
    src = C.get("source", ["", ""])
    return (f'<div class="row head"><div class=pg style="width:{w}px"><div class=ln></div><div class=fill></div>{dots}'
            f'<img class=mini src="{SPR["base"]}"></div><div class=ttl><b>{it["title"]}</b><span>{it["sub"]}</span></div>'
            f'<div class=src>{src[0]}<span>{src[1]}</span></div></div>')

html = [f'<!doctype html><meta charset=utf-8><style>{CSS}</style><body><div class=brand>{BRAND}</div>']
h = C["hook"]
html.append('<div class=scene id=s0><div class=tag>' + h["tag"] + '</div>' +
            "".join(f'<div class=hl style="top:{480 + k * 156}px">{l}</div>' for k, l in enumerate(h["lines"])) + '</div>')
for i, it in enumerate(C["items"]):
    kind = it.get("type", "chat")
    meter = f'<div class=meter>{it.get("meter", "쓸모" if kind == "chat" else "진행")}<div class=mb><b></b></div></div>'
    if kind == "chat":
        body = ('<div class=me></div><div class=dots><i></i><i></i><i></i></div><div class=ai></div><div class=stamp></div>'
                '<div class=inp><i>+</i><div class=tx></div><div class=send>↑</div></div>')
        bar = "새 대화"
    else:
        rows = "".join(f'<div class=li><div class=k>{r.get("k", j + 1)}</div><div><b>{r["t"]}</b><span>{r.get("d", "")}</span>'
                       f'<div class=lb></div></div><div class=ok>✓</div></div>' for j, r in enumerate(it["rows"]))
        chip = f'<div class=chip>{it["chip"][0]}<b>{it["chip"][1]}</b></div>' if it.get("chip") else ""
        body = f'<div class=lst>{rows}</div>'
        bar = it.get("bar", "체크리스트")
    tag = it.get("tag", "그대로 따라 쳐 보세요" if kind == "chat" else "저장해 두고 하나씩")
    chip_html = chip if kind != 'chat' else ''
    html.append(f'''<div class=scene id=s{i+1}><div class=card>{chip_html}{head(i, it)}
<div class="row how"><span class=pill></span><span class=howt></span>{meter}</div>
<div class=win><div class=bar><i></i>{bar}</div><div class=load></div>{body}</div>
<div class=tags><span><i></i>{tag}</span></div></div><div class=cap></div></div>''')
sm = C["summary"]
rows = "".join(f'<div class="row item" style="height:{168 if N == 3 else 136}px"><u><b>✓</b><em></em></u><div><b>{a}</b><span>{b}</span></div><s>OK</s></div>'
               for a, b in sm["rows"])
html.append(f'''<div class=scene id=s{N+1}><div class=card style="top:{300 if N == 3 else 260}px"><div class=shead><i></i>{sm["head"]}<span class=cnt></span></div>
<div class=segs>{''.join('<i><b></b></i>' for _ in sm['rows'])}</div>{rows}<div class=foot></div></div><div class=cap>{sm["cap"]}</div></div>''')
html.append('<div id=sh></div><img id=sl>')
html.append("<script>const C=" + json.dumps(C, ensure_ascii=False) + ";const SPR=" + json.dumps(SPR) + f";const GAP={GAP};\n" +
            open(os.path.join(HERE, "timeline.js"), encoding="utf-8").read() + "</script>")
open(os.path.join(HERE, "page.html"), "w", encoding="utf-8").write("\n".join(html))
print("page.html 준비됨: 항목", N, "개")
