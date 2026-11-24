// honu_dev 카드뉴스 만들기 (이 폴더에서 실행)
//   node render.js                 → shots/01.png …  정지 그림 (검수용, 영상의 마지막 모습)
//   node render.js --video         → shots/01.mp4 …  모션 카드뉴스 (올리는 것, 한 장에 5초)
//   --secs=4,6,6,5,6,7,5   장마다 영상 길이(초, 4~8). 안 쓰면 모두 5초
//   --pages=Main,S2,S3,S4,S5,S8,S9   쓸 장과 순서. 안 쓰면 아래 PAGES 목록
//   2026-11-24 채널 주인: 인스타가 '모두 5초인 영상 8~9개 묶음'을 5번 연속 스팸으로 막음 → 장마다 길이를 다르게, 6~7장으로 시험 중
//   --theme=sun|coral|pink|orange|lav|grid|night|forest  배경 바꾸기 (안 쓰면 노을)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const arg = k => (process.argv.find(a => a.startsWith(`--${k}=`)) || '').split('=')[1];
const PAGES = arg('pages') ? arg('pages').split(',') : ['Main','S2','S3','S4','S5','S6','S7','S8','S9']; // 장 수가 바뀌면 이 목록도 맞춘다
const SECONDS = 5, FPS = 30;
const SECS = arg('secs') ? arg('secs').split(',').map(Number) : PAGES.map(() => SECONDS);
if (SECS.length !== PAGES.length || SECS.some(x => !(x >= 4 && x <= 8)))
  throw new Error(`--secs 는 장 수(${PAGES.length})만큼, 4~8초로 준다: ${SECS.join(',')}`);
const video = process.argv.includes('--video');
const theme = arg('theme');
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
      await p.evaluate(seek, SECS[i] * 1000);
      await p.screenshot({ path: `shots/${name}.png` });
      continue;
    }
    const tmp = `shots/${name}.tmp.mp4`;
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(FPS), '-i', '-',
      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', tmp], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = 0; f < SECS[i] * FPS; f++) {
      await p.evaluate(seek, (f / FPS) * 1000);
      ff.stdin.write(await p.screenshot({ type: 'jpeg', quality: 92 }));
    }
    ff.stdin.end();
    const code = await new Promise(r => ff.on('close', r));
    if (code !== 0) throw new Error(`${name} 영상 만들기 실패`);
    fs.renameSync(tmp, `shots/${name}.mp4`);
  }
  await b.close();
  console.log(video ? '영상' : '그림', PAGES.length + '장 완성 → shots/', video ? `(길이 ${SECS.join(',')}초)` : '');
})();
