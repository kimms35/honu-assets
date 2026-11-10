const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  for (const n of ['Main','S2','S3','S4','S5','S6','S7','S8','S9']) {
    let h = fs.readFileSync(`project/${n}.dc.html`, 'utf8');
    h = h.replace('<script src="./support.js"></script>', "<style>@font-face{font-family:'Noto Sans KR';src:local('Noto Sans CJK KR Black');font-weight:900}@font-face{font-family:'Noto Sans KR';src:local('Noto Sans CJK KR Bold');font-weight:700}x-dc{display:block}</style>").replace(/<link rel="stylesheet"[^>]*>/, '');
    await p.setContent(h);
    await p.waitForTimeout(200);
    await p.screenshot({ path: `shots/${n}.png` });
  }
  await b.close();
})();
