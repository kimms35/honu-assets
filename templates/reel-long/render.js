// 사용법 (reel-long 폴더에서):
//   python3 gen.py 문구.json                 → page.html
//   node render.js stills [초 ...]           → out/still_<초>.png (초를 안 주면 장면마다 자동으로 고른 순간)
//   node render.js video                     → out/reel.mp4 (1080x1920, 30fps, 음악 없음)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
const HERE = __dirname, OUT = path.join(HERE, 'out'), FPS = 30;
fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(HERE, 'page.html'));
  await p.evaluate(() => document.fonts.ready);
  const total = await p.evaluate(() => window.TOTAL);
  if (process.argv[2] === 'stills') {
    let ts = process.argv.slice(3).map(Number);
    if (!ts.length) {
      const n = Math.round((total - 10.5) / 13);
      ts = [2.5];
      for (let i = 0; i < n; i++) { const s = 4 + 13 * i; ts.push(s + 4.2, s + 8.0, s + 12.2); }
      ts.push(total - .5);
    }
    for (const t of ts) {
      await p.evaluate(x => setT(x), t);
      await p.screenshot({ path: path.join(OUT, `still_${t.toFixed(1)}.png`) });
    }
    console.log('stills', ts.length, 'total', total);
  } else {
    const tmp = path.join(OUT, 'reel.tmp.mp4');
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', tmp], { stdio: ['pipe', 'inherit', 'inherit'] });
    const N = Math.round(total * FPS);
    for (let k = 0; k < N; k++) {
      await p.evaluate(t => setT(t), k / FPS);
      const buf = await p.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    ff.stdin.end();
    const code = await new Promise(r => ff.on('close', r));
    if (code === 0) fs.renameSync(tmp, path.join(OUT, 'reel.mp4'));
    console.log('frames', N, 'total', total, 'ffmpeg', code);
  }
  await b.close();
})();
