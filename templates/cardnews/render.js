// 사용법: (이 폴더에서) mkdir -p shots && node render.js  →  shots/01.png … 에 그림이 생김
const { chromium } = require('playwright');
const path = require('path');
const PAGES = ['Main','S2','S3','S4','S5','S6','S7','S8','S9']; // 장 수가 바뀌면 이 목록도 맞춘다
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  for (let i = 0; i < PAGES.length; i++) {
    await p.goto('file://' + path.resolve('project', PAGES[i] + '.html'));
    await p.waitForTimeout(250);
    await p.screenshot({ path: `shots/${String(i + 1).padStart(2, '0')}.png` });
  }
  await b.close();
})();
