// honu_dev 카드뉴스 만들기 (이 폴더에서 실행)
//   node render.js                 → shots/01.png …  정지 그림 (검수용, 영상의 마지막 모습)
//   node render.js --video         → shots/01.mp4 …  모션 카드뉴스 (올리는 것, 한 장에 5초)
//   --theme=sun|coral|pink|orange|lav|grid|night|forest  배경 바꾸기 (안 쓰면 노을)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const PAGES = ['Main','S2','S3','S4','S5','S6','S7','S8','S9']; // 장 수가 바뀌면 이 목록도 맞춘다
const SECONDS = 5, FPS = 30;
const video = process.argv.includes('--video');
const theme = (process.argv.find(a => a.startsWith('--theme=')) || '').split('=')[1];
const seek = ms => { for (const a of document.getAnimations()) { a.pause(); a.currentTime = ms; } };
(async () => {
  fs.mkdirSync('shots', { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  for (let i = 0; i < PAGES.length; i++) {
    const name = String(i + 1).padStart(2, '0');
    await p.goto('file://' + path.resolve('project', PAGES[i] + '.html'));
    await p.evaluate(t => { if (t) document.body.classList.add('t-' + t); }, theme);
    await p.waitForTimeout(250);
    if (!video) {
      await p.evaluate(() => document.body.classList.add('still'));
      await p.evaluate(seek, SECONDS * 1000);
      await p.screenshot({ path: `shots/${name}.png` });
      continue;
    }
    const tmp = `shots/${name}.tmp.mp4`;
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(FPS), '-i', '-',
      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', tmp], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = 0; f < SECONDS * FPS; f++) {
      await p.evaluate(seek, (f / FPS) * 1000);
      ff.stdin.write(await p.screenshot({ type: 'jpeg', quality: 92 }));
    }
    ff.stdin.end();
    const code = await new Promise(r => ff.on('close', r));
    if (code !== 0) throw new Error(`${name} 영상 만들기 실패`);
    fs.renameSync(tmp, `shots/${name}.mp4`);
  }
  await b.close();
  console.log(video ? '영상' : '그림', PAGES.length + '장 완성 → shots/');
})();
