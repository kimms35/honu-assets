/* 모션 부품 모음 (2026-11-26, 인기 릴스 20개에서 모은 움직임을 우리 방식으로 다시 만든 것)
   쓰는 법: project/index.html 에 motions.css, gsap.min.js, motions.js 를 차례로 넣고
     const tl = gsap.timeline({paused:true});
     M.capGrow(tl, 0.2, {words:['아이폰으로','찍은','영상,']});
     M.tagCount(tl, 1.0, {x:600, y:700, from:4874, to:10000});
   모든 함수는 (tl, at, opts) 를 받아 자기 DOM 을 opts.parent(기본 #stage, 없으면 #root)에 만들고
   tl 의 at 초에 움직임을 넣는다. 만든 요소 묶음을 돌려준다.
   HyperFrames 규칙: Math.random·setTimeout·CSS animation 을 쓰지 않는다. 숫자는 onUpdate 로 그린다.
   글자 크기·안전 영역(가로 60~1020, 세로 140~1560) 규칙은 그날 화면에서 지킨다. */
(function(){
const M = {};
const host = o => (o && o.parent) || document.getElementById('stage') || document.getElementById('root');
function el(tag, cls, parent, style, html){
  const e = document.createElement(tag);
  if(cls) e.className = cls;
  if(style) Object.assign(e.style, style);
  if(html != null) e.innerHTML = html;
  parent.appendChild(e);
  return e;
}
const cv = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim() || '#FFCE54';
const fmt = n => Math.round(n).toLocaleString('en-US');
// 같은 입력이면 같은 값 (Math.random 대신)
function rng(seed){ let s = seed >>> 0 || 1; return () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296; }
function svg(parent, w, h, style){
  const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  s.setAttribute('width', w); s.setAttribute('height', h); s.setAttribute('viewBox', `0 0 ${w} ${h}`);
  s.style.position = 'absolute'; Object.assign(s.style, style || {});
  parent.appendChild(s); return s;
}
function sv(parent, tag, attrs){
  const e = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for(const k in attrs) e.setAttribute(k, attrs[k]);
  parent.appendChild(e); return e;
}
const STAR = 'M50 4 61 37 96 37 68 58 79 92 50 71 21 92 32 58 4 37 39 37Z';

/* 1. 자막 칩이 낱말 단위로 자람. opts: words[], gap(낱말 간격 초), x, y */
M.capGrow = function(tl, at, o){
  const p = host(o), gap = o.gap || 0.32;
  const chip = el('div', 'm-capchip', p, {left:(o.x||64)+'px', top:(o.y||240)+'px'});
  const ws = o.words.map(w => el('span', '', chip, null, w));
  tl.fromTo(chip, {scaleX:0, opacity:0}, {scaleX:1, opacity:1, duration:0.25, ease:'back.out(2)'}, at);
  ws.forEach((w, i) => tl.fromTo(w, {opacity:0, y:20}, {opacity:1, y:0, duration:0.18, ease:'power2.out'}, at + 0.1 + i*gap));
  return {chip, ws};
};

/* 2. 매달린 태그 카운트업. opts: x,y, from,to, label(앞 글자), suffix */
M.tagCount = function(tl, at, o){
  const p = host(o);
  const tag = el('div', 'm-tag', p, {left:o.x+'px', top:o.y+'px'}, `<b>${o.label||''}${fmt(o.from)}${o.suffix||''}</b>`);
  const b = tag.querySelector('b'), c = {v:o.from};
  tl.fromTo(tag, {opacity:0, rotation:-35, y:-80}, {opacity:1, rotation:0, y:0, duration:0.9, ease:'elastic.out(1,0.35)'}, at);
  tl.fromTo(c, {v:o.from}, {v:o.to, duration:o.dur||1.4, ease:'power2.out',
    onUpdate:()=>{ b.textContent = (o.label||'') + fmt(c.v) + (o.suffix||''); }}, at + 0.2);
  tl.to(tag, {rotation:6, duration:0.18, yoyo:true, repeat:1, ease:'sine.inOut'}, at + 0.2 + (o.dur||1.4));
  return {tag};
};

/* 3. 도장 쾅. opts: x,y, text, sub(둥근 도장 아랫줄), round, color */
M.stamp = function(tl, at, o){
  const p = host(o);
  const s = el('div', 'm-stamp' + (o.round?' round':''), p, {left:o.x+'px', top:o.y+'px'},
    o.round ? `${o.text}<small>${o.sub||''}</small>` : o.text);
  if(o.color){ s.style.color = o.color; s.style.borderColor = o.color; }
  tl.fromTo(s, {opacity:0, scale:3, rotation:-18}, {opacity:1, scale:1, rotation:o.rot==null?-8:o.rot, duration:0.28, ease:'power4.in'}, at);
  const cam = document.getElementById('cam');
  if(cam) tl.fromTo(cam, {x:0}, {x:10, duration:0.05, yoyo:true, repeat:5, ease:'none'}, at + 0.28);
  return {s};
};

/* 4. 가격이 오르다 취소선 → 0원 도장. opts: x,y, from,to */
M.priceToZero = function(tl, at, o){
  const p = host(o);
  const pr = el('div', 'm-price', p, {left:o.x+'px', top:o.y+'px'}, '₩' + fmt(o.from));
  const c = {v:o.from};
  tl.fromTo(pr, {opacity:0, y:40}, {opacity:1, y:0, duration:0.3}, at);
  tl.fromTo(c, {v:o.from}, {v:o.to, duration:1.0, ease:'power2.out', onUpdate:()=>{ pr.textContent = '₩' + fmt(c.v); }}, at + 0.2);
  const st = el('div', 'm-strike', p, {left:(o.x-20)+'px', top:(o.y+56)+'px', width:'600px'});
  tl.fromTo(st, {scaleX:0}, {scaleX:1, duration:0.3, ease:'power2.out'}, at + 1.3);
  tl.to(pr, {opacity:0.35, duration:0.2}, at + 1.5);
  const zero = el('div', 'm-price', p, {left:o.x+'px', top:(o.y+150)+'px', color:'var(--m-hi)'}, '₩0');
  tl.fromTo(zero, {opacity:0, scale:0.4}, {opacity:1, scale:1, duration:0.35, ease:'back.out(3)'}, at + 1.6);
  const s = M.stamp(tl, at + 2.0, {parent:p, x:o.x + 330, y:o.y + 170, text:o.stamp||'0원', sub:o.sub||'전부 무료', round:true});
  return {pr, st, zero, s};
};

/* 5. 순위 줄이 위로 올라가 1위에 붙기. opts: y, rows[](이름, 맨 아래가 올라감), fromRank */
M.rankClimb = function(tl, at, o){
  const p = host(o), y0 = o.y || 560, H = 112;
  const box = el('div', 'm-rank', p, {top:y0+'px'});
  const names = o.rows;
  const rows = names.map((n, i) => el('div', 'm-row', box, {top:(i*H)+'px'}, `<i>${i+1}</i>${n}`));
  const hot = rows[rows.length-1]; hot.classList.add('hot');
  hot.querySelector('i').textContent = o.fromRank || rows.length;
  rows.forEach((r, i) => tl.fromTo(r, {opacity:0, x:-60}, {opacity:1, x:0, duration:0.25}, at + i*0.06));
  const t1 = at + 0.9;
  tl.to(hot, {backgroundColor:'#3A2A10', duration:0.2}, t1);
  tl.to(hot, {y:-(rows.length-1)*H, duration:0.8, ease:'power3.inOut'}, t1 + 0.2);
  rows.slice(0,-1).forEach((r, i) => {
    tl.to(r, {y:H, duration:0.8, ease:'power3.inOut'}, t1 + 0.2);
    tl.call(() => { r.querySelector('i').textContent = i + 2; }, null, t1 + 0.6);
  });
  tl.call(() => { hot.querySelector('i').textContent = 1; }, null, t1 + 0.6);
  tl.to(hot, {backgroundColor:cv('--m-hi'), color:'#1A1220', duration:0.25}, t1 + 1.0);
  tl.fromTo(hot, {scale:1}, {scale:1.06, duration:0.15, yoyo:true, repeat:1}, t1 + 1.0);
  return {rows, hot};
};

/* 6. 그래프 끝 막대만 솟기 + 손그림 원. opts: x,y, n, h[](생략 시 낮은 값), spikeH */
M.barSpike = function(tl, at, o){
  const p = host(o), n = o.n || 12, r = rng(7);
  const bars = el('div', 'm-bars', p, {left:(o.x||120)+'px', top:(o.y||1100)+'px', height:'0px'});
  const ds = [];
  for(let i=0;i<n;i++){
    const h = o.h ? o.h[i] : 40 + Math.round(r()*60);
    const d = el('div', i===n-1?'spike':'', bars, {height:h+'px'});
    ds.push(d);
    if(i < n-1) tl.fromTo(d, {scaleY:0}, {scaleY:1, duration:0.3, ease:'power2.out'}, at + i*0.04);
  }
  const last = ds[n-1], H = o.spikeH || 420;
  last.style.height = H+'px';
  tl.fromTo(last, {scaleY:0.1}, {scaleY:1, duration:0.6, ease:'back.out(1.6)'}, at + n*0.04 + 0.3);
  const ring = el('div', 'm-ring', p, {left:((o.x||120) + (n-1)*60 - 40)+'px', top:((o.y||1100) - H - 50)+'px', width:'130px', height:(H+90)+'px'});
  tl.fromTo(ring, {opacity:0, scale:1.4, rotation:-10}, {opacity:1, scale:1, rotation:-4, duration:0.3, ease:'power2.out'}, at + n*0.04 + 1.0);
  return {bars, last, ring};
};

/* 7. 1P vs 2P 대결 막대. opts: y, a:{name,to,color}, b:{name,to,color}, max */
M.versus = function(tl, at, o){
  const p = host(o);
  const box = el('div', 'm-vs', p, {top:(o.y||700)+'px'});
  const lane = (s, col) => {
    const L = el('div', 'lane', box);
    const f = el('div', 'fill', L, {background:col});
    el('div', 'lbl', L, null, s.name);
    const n = el('div', 'num', L, null, '0');
    return {f, n};
  };
  const A = lane(o.a, o.a.color||'var(--m-blue)'), B = lane(o.b, o.b.color||'var(--m-bad)');
  const max = o.max || Math.max(o.a.to, o.b.to) * 1.05, c = {a:0, b:0};
  tl.fromTo(box, {opacity:0, y:40}, {opacity:1, y:0, duration:0.3}, at);
  tl.to(c, {a:o.a.to, b:o.b.to, duration:2.0, ease:'power1.inOut', onUpdate:()=>{
    A.f.style.width = (c.a/max*100)+'%'; B.f.style.width = (c.b/max*100)+'%';
    A.n.textContent = fmt(c.a); B.n.textContent = fmt(c.b);
  }}, at + 0.3);
  return {box, A, B};
};

/* 8. 선버스트 배경 + 로딩 원 → 별 → 반짝이 → 미니 막대 차오름. opts: x,y(별 중심), bars(10) */
M.loaderStar = function(tl, at, o){
  const p = host(o), cx = o.x || 540, cy = o.y || 900;
  const sun = el('div', 'm-sunburst', p, {left:cx+'px', top:cy+'px'});
  tl.fromTo(sun, {opacity:0}, {opacity:1, duration:0.4}, at);
  tl.fromTo(sun, {rotation:0}, {rotation:40, duration:o.spin || 6, ease:'none'}, at);
  const ld = el('div', 'm-loader', p, {left:(cx-80)+'px', top:(cy-80)+'px'});
  tl.fromTo(ld, {opacity:0, rotation:0}, {opacity:1, rotation:540, duration:0.9, ease:'none'}, at);
  tl.to(ld, {opacity:0, scale:0.3, duration:0.15}, at + 0.9);
  const st = svg(p, 220, 220, {left:(cx-110)+'px', top:(cy-110)+'px'});
  sv(st, 'path', {d:STAR, transform:'scale(2.2)', fill:'var(--m-hi)', stroke:'#1A1220', 'stroke-width':'3'});
  tl.fromTo(st, {opacity:0, scale:0, rotation:-90}, {opacity:1, scale:1, rotation:0, duration:0.45, ease:'back.out(2.5)'}, at + 0.95);
  const r = rng(11);
  for(let i=0;i<10;i++){
    const a = i/10*Math.PI*2, d = 170 + r()*60;
    const s = el('div', 'm-spark', p, {left:cx+'px', top:cy+'px'});
    tl.fromTo(s, {opacity:1, x:0, y:0, scale:1}, {opacity:0, x:Math.cos(a)*d, y:Math.sin(a)*d, scale:0.3, rotation:90, duration:0.6, ease:'power2.out'}, at + 1.0);
  }
  const bars = el('div', 'm-bars', p, {left:(cx-330)+'px', top:(cy+260)+'px', height:'0px'});
  const n = o.bars || 10;
  for(let i=0;i<n;i++){
    const h = 40 + i*14;
    const d = el('div', '', bars, {height:h+'px', background:'var(--m-hi)'});
    tl.fromTo(d, {scaleY:0}, {scaleY:1, duration:0.25, ease:'power2.out'}, at + 1.3 + i*0.07);
  }
  return {sun, st, bars};
};

/* 9. 아이콘이 쏟아지며 격자를 채우고 숫자가 따라 오름. opts: x,y, cols,rows, to, colors[] */
M.iconRain = function(tl, at, o){
  const p = host(o), cols = o.cols || 8, rows = o.rows || 6, r = rng(3);
  const cs = o.colors || ['#FF7A1A','#FFCE54','#5FB2FF','#53D68A','#FF5A5A','#B58CFF'];
  const x0 = o.x || 140, y0 = o.y || 640, n = cols*rows, ics = [];
  for(let i=0;i<n;i++){
    const ic = el('div', 'm-icon', p, {left:(x0 + (i%cols)*100)+'px', top:(y0 + Math.floor(i/cols)*100)+'px', background:cs[Math.floor(r()*cs.length)]});
    ics.push(ic);
    tl.fromTo(ic, {opacity:0, y:-400 - r()*300}, {opacity:1, y:0, duration:0.5, ease:'bounce.out'}, at + i*0.025);
  }
  let tag = null;
  if(o.to) tag = M.tagCount(tl, at + 0.4, {parent:p, x:(o.tagX||620), y:(o.tagY||y0 + rows*100 + 90), from:0, to:o.to, suffix:o.suffix||'개', dur:n*0.025});
  return {ics, tag};
};

/* 10. 서류가 한 장씩 쌓여 기둥이 됨. opts: x, base(바닥 y), n, count(태그 숫자) */
M.docStack = function(tl, at, o){
  const p = host(o), n = o.n || 30, x = o.x || 360, base = o.base || 1400, r = rng(5), docs = [];
  for(let i=0;i<n;i++){
    const d = el('div', 'm-doc', p, {left:(x + (r()-0.5)*40)+'px', top:(base - (i+1)*26)+'px', transform:`rotate(${((r()-0.5)*8).toFixed(1)}deg)`});
    docs.push(d);
    tl.fromTo(d, {opacity:0, y:-300}, {opacity:1, y:0, duration:0.22, ease:'power3.in'}, at + i*0.05);
  }
  if(o.count) M.tagCount(tl, at + 0.2, {parent:p, x:x + 420, y:base - n*13, from:0, to:o.count, suffix:o.suffix||'개', dur:n*0.05});
  return {docs};
};

/* 11. 폰 틀은 그대로, 화면 속만 바뀜. opts: x,y, pages[](html) , every(초) */
M.phoneStory = function(tl, at, o){
  const p = host(o), every = o.every || 1.2;
  const ph = el('div', 'm-phone', p, {left:(o.x||320)+'px', top:(o.y||560)+'px'});
  const scr = el('div', 'scr', ph);
  const pages = o.pages.map((h, i) => el('div', 'pg', scr, {opacity:i?0:1, background:(o.bgs||[])[i]||'transparent'}, h));
  tl.fromTo(ph, {opacity:0, y:120, rotation:-6}, {opacity:1, y:0, rotation:0, duration:0.4, ease:'back.out(1.6)'}, at);
  pages.forEach((pg, i) => { if(!i) return;
    const t = at + 0.4 + i*every;
    tl.fromTo(pg, {opacity:0, y:i%2?300:0, scale:i%2?1:1.15}, {opacity:1, y:0, scale:1, duration:0.35, ease:'power3.out'}, t);
    tl.to(pages[i-1], {opacity:0, duration:0.2}, t + 0.15);
  });
  return {ph, pages};
};

/* 12. 물건이 포물선을 그리며 기기 사이를 날아감. opts: from:{x,y}, to:{x,y}, lift(곡선 높이) */
M.arcThrow = function(tl, at, o){
  const p = host(o), a = o.from, b = o.to, lift = o.lift || 360;
  const lap = el('div', 'm-laptop', p, {left:(b.x-210)+'px', top:(b.y-80)+'px'});
  tl.fromTo(lap, {opacity:0, x:300}, {opacity:1, x:0, duration:0.4, ease:'power3.out'}, at);
  const mx = (a.x+b.x)/2, my = Math.min(a.y, b.y) - lift;
  const sg = svg(p, 1080, 1920, {left:'0', top:'0'});
  const path = sv(sg, 'path', {d:`M${a.x} ${a.y} Q${mx} ${my} ${b.x} ${b.y}`, class:'m-dash'});
  const len = 2000;
  tl.fromTo(path, {strokeDashoffset:len, opacity:0}, {strokeDashoffset:0, opacity:0.6, duration:0.6, ease:'power1.out'}, at + 0.4);
  const box = el('div', 'm-box', p, {left:(a.x-60)+'px', top:(a.y-50)+'px'});
  const c = {t:0};
  tl.fromTo(box, {opacity:0, scale:0.3}, {opacity:1, scale:1, duration:0.2}, at + 0.4);
  tl.fromTo(c, {t:0}, {t:1, duration:0.9, ease:'power1.inOut', onUpdate:()=>{
    const t = c.t, x = (1-t)*(1-t)*a.x + 2*(1-t)*t*mx + t*t*b.x, y = (1-t)*(1-t)*a.y + 2*(1-t)*t*my + t*t*b.y;
    box.style.transform = `translate(${(x-a.x).toFixed(2)}px,${(y-a.y).toFixed(2)}px) rotate(${t*360}deg) scale(${1 - t*0.3})`;
  }}, at + 0.6);
  tl.fromTo(lap, {scale:1}, {scale:1.05, duration:0.12, yoyo:true, repeat:1}, at + 1.5);
  return {box, lap, path};
};

/* 13. 커서 여러 개가 동시에 토글을 켬. opts: n(커서 수, 3) */
M.multiCursor = function(tl, at, o){
  const p = host(o), n = o.n || 3, cols = ['var(--m-accent)','var(--m-blue)','var(--m-good)','var(--m-hi)'];
  const win = el('div', 'm-win', p);
  tl.fromTo(win, {opacity:0, scale:0.9}, {opacity:1, scale:1, duration:0.3, ease:'back.out(1.6)'}, at);
  const tg = [], cur = [];
  for(let i=0;i<4;i++){
    el('div', 'm-t', win, {position:'absolute', left:'50px', top:(70+i*140)+'px', fontSize:'44px'}, ['알림','자동 저장','동기화','백업'][i]);
    const t = el('div', 'm-toggle', win, {left:'650px', top:(60+i*140)+'px'}, '<i></i>');
    tg.push(t);
  }
  for(let k=0;k<n;k++){
    const s = svg(p, 64, 64, {left:'540px', top:'1500px'});
    sv(s, 'path', {d:'M6 4 L6 52 L20 40 L30 60 L40 55 L30 36 L50 36 Z', fill:cols[k%cols.length], stroke:'#1A1220', 'stroke-width':'4'});
    cur.push(s);
    const ti = k % 4, tx = 110 + 650 + 40, ty = 620 + 60 + ti*140 + 30, t0 = at + 0.4 + k*0.15;
    tl.fromTo(s, {x:0, y:0, opacity:0}, {x:tx-540, y:ty-1500, opacity:1, duration:0.7, ease:'power2.inOut'}, t0);
    tl.to(s, {scale:0.8, duration:0.08, yoyo:true, repeat:1}, t0 + 0.7);
    tl.to(tg[ti], {backgroundColor:cv('--m-good'), duration:0.15}, t0 + 0.75);
    tl.to(tg[ti].querySelector('i'), {x:56, duration:0.15}, t0 + 0.75);
  }
  return {win, tg, cur};
};

/* 14. 한 선이 여러 갈래로 갈라졌다 합쳐짐(지하철 노선). opts: y, n(갈래 수) */
M.branchLines = function(tl, at, o){
  const p = host(o), y = o.y || 1000, n = o.n || 3, cols = ['var(--m-accent)','var(--m-blue)','var(--m-good)','var(--m-hi)'];
  const sg = svg(p, 1080, 1920, {left:'0', top:'0'});
  const main = sv(sg, 'path', {d:`M80 ${y} L300 ${y}`, class:'m-rail', stroke:'var(--m-ink)'});
  tl.fromTo(main, {strokeDasharray:'240 2000', strokeDashoffset:240}, {strokeDashoffset:0, duration:0.4}, at);
  for(let i=0;i<n;i++){
    const dy = (i - (n-1)/2) * 200;
    const d = `M300 ${y} C380 ${y} 380 ${y+dy} 460 ${y+dy} L640 ${y+dy} C720 ${y+dy} 720 ${y} 800 ${y} L1000 ${y}`;
    const ln = sv(sg, 'path', {d, class:'m-rail', stroke:cols[i%cols.length]});
    tl.fromTo(ln, {strokeDasharray:'900 3000', strokeDashoffset:900}, {strokeDashoffset:0, duration:1.2, ease:'power1.inOut'}, at + 0.4 + i*0.12);
    const st = el('div', 'm-stn', p, {left:(550-22)+'px', top:(y+dy-22)+'px'});
    tl.fromTo(st, {scale:0}, {scale:1, duration:0.25, ease:'back.out(3)'}, at + 0.9 + i*0.12);
  }
  return {sg};
};

/* 15. 티어표 줄에 카드가 날아와 꽂힘. opts: y, tiers['S','A','B','C'], items:[{t:'S',name}] */
M.tierDrop = function(tl, at, o){
  const p = host(o), y0 = o.y || 560, tiers = o.tiers || ['S','A','B','C'];
  const tc = {S:'#FF5A5A', A:'#FF9E3D', B:'#FFCE54', C:'#53D68A'};
  const rowY = {};
  tiers.forEach((t, i) => {
    const r = el('div', 'm-tier', p, {top:(y0 + i*170)+'px'}, `<b style="background:${tc[t]||'#ccc'}">${t}</b>`);
    rowY[t] = y0 + i*170; rowY[t+'n'] = 0;
    tl.fromTo(r, {opacity:0, x:-80}, {opacity:1, x:0, duration:0.25}, at + i*0.06);
  });
  o.items.forEach((it, k) => {
    const idx = rowY[it.t+'n']++;
    const c = el('div', 'm-chip', p, {left:(240 + idx*180)+'px', top:(rowY[it.t] + 20)+'px'}, it.name);
    tl.fromTo(c, {opacity:0, y:-500, rotation:-20}, {opacity:1, y:0, rotation:0, duration:0.4, ease:'back.out(1.4)'}, at + 0.5 + k*0.3);
  });
  return {};
};

/* 16. 아래 선반에 썸네일이 한 권씩 꽂히는 진행 표시. opts: y(선반 y), n, at들은 marks[] 로 각각 */
M.shelf = function(tl, at, o){
  const p = host(o), y = o.y || 1380, n = o.n || 6, cs = o.colors || ['#FF7A1A','#5FB2FF','#53D68A','#FFCE54','#B58CFF','#FF5A5A'];
  const sh = el('div', 'm-shelf', p, {top:y+'px'});
  tl.fromTo(sh, {scaleX:0}, {scaleX:1, duration:0.3, transformOrigin:'0 50%'}, at);
  const books = [];
  for(let i=0;i<n;i++){
    const b = el('div', 'm-book', p, {left:(110 + i*140)+'px', top:(y-150)+'px', background:cs[i%cs.length]}, String(i+1));
    books.push(b);
    const t = (o.marks && o.marks[i] != null) ? o.marks[i] : at + 0.4 + i*0.35;
    tl.fromTo(b, {opacity:0, y:-260}, {opacity:1, y:0, duration:0.3, ease:'bounce.out'}, t);
  }
  return {sh, books};
};

/* 17. 금고 다이얼이 돌고 문이 열림. opts: count(안쪽 태그 숫자) */
M.vaultOpen = function(tl, at, o){
  const p = host(o);
  const v = el('div', 'm-vault', p);
  const inside = el('div', 'm-t', v, {position:'absolute', inset:'0', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'72px'}, o.inside || '노트 40개');
  const door = el('div', 'm-door', v);
  const dial = el('div', 'm-dial', door);
  tl.fromTo(v, {opacity:0, y:60}, {opacity:1, y:0, duration:0.3}, at);
  tl.fromTo(dial, {rotation:0}, {rotation:-270, duration:0.9, ease:'power2.inOut'}, at + 0.3);
  tl.to(dial, {rotation:-180, duration:0.4, ease:'power2.inOut'}, at + 1.2);
  tl.to(door, {rotationY:-100, duration:0.7, ease:'power3.inOut', transformPerspective:1400}, at + 1.7);
  tl.fromTo(inside, {scale:0.8, opacity:0}, {scale:1, opacity:1, duration:0.4, ease:'back.out(2)'}, at + 2.0);
  return {v, door, dial};
};

/* 18. 점과 선이 퍼지며 그래프가 그려지고 초 타이머가 오름. opts: nodes(24), sec(1.71) */
M.graphGrow = function(tl, at, o){
  const p = host(o), N = o.nodes || 24, r = rng(17);
  const sg = svg(p, 1080, 1920, {left:'0', top:'0'});
  const pts = [];
  for(let i=0;i<N;i++) pts.push([180 + r()*720, 640 + r()*640]);
  const lines = [];
  for(let i=1;i<N;i++){
    const j = Math.floor(r()*i);
    lines.push(sv(sg, 'line', {x1:pts[j][0], y1:pts[j][1], x2:pts[i][0], y2:pts[i][1], class:'m-gline'}));
  }
  const nodes = pts.map(q => sv(sg, 'circle', {cx:q[0], cy:q[1], r:16, class:'m-gnode'}));
  nodes.forEach((n, i) => tl.fromTo(n, {opacity:0, scale:0, transformOrigin:'50% 50%'}, {opacity:1, scale:1, duration:0.2, ease:'back.out(3)'}, at + 0.2 + i*0.05));
  lines.forEach((l, i) => tl.fromTo(l, {opacity:0}, {opacity:0.55, duration:0.2}, at + 0.3 + i*0.05));
  const tm = el('div', 'm-timer', p, {left:'90px', top:'420px'}, '0.00');
  const c = {v:0};
  tl.fromTo(tm, {scale:0}, {scale:1, duration:0.25, ease:'back.out(2)'}, at);
  tl.fromTo(c, {v:0}, {v:o.sec || 1.71, duration:0.2 + N*0.05, ease:'none', onUpdate:()=>{ tm.textContent = c.v.toFixed(2); }}, at + 0.2);
  return {sg, tm};
};

/* 19. 똑같은 화면 9장을 격자로 깔기("다 비슷하다") */
M.sameGrid = function(tl, at, o){
  const p = host(o), x0 = o.x || 90, y0 = o.y || 640, out = [];
  for(let i=0;i<9;i++){
    const s = el('div', 'm-same', p, {left:(x0 + (i%3)*310)+'px', top:(y0 + Math.floor(i/3)*240)+'px'});
    out.push(s);
    tl.fromTo(s, {opacity:0, scale:0.6}, {opacity:1, scale:1, duration:0.25, ease:'back.out(2)'}, at + i*0.08);
  }
  return {out};
};

/* 20. 이정표: 상황별로 갈라지는 표지판. opts: signs:[{text,color}] */
M.signpost = function(tl, at, o){
  const p = host(o), x = o.x || 520, top = o.y || 700;
  const post = el('div', 'm-post', p, {left:x+'px', top:top+'px', height:'760px'});
  tl.fromTo(post, {scaleY:0, transformOrigin:'50% 100%'}, {scaleY:1, duration:0.35, ease:'power2.out'}, at);
  (o.signs || []).forEach((s, i) => {
    const left = i % 2 === 0;
    const g = el('div', 'm-sign', p, {top:(top + 40 + i*150)+'px', background:s.color||'var(--m-hi)', left: left ? (x - 420)+'px' : (x + 10)+'px',
      clipPath: left ? 'polygon(8% 0,100% 0,100% 100%,8% 100%,0 50%)' : 'polygon(0 0,92% 0,100% 50%,92% 100%,0 100%)', width:'440px', textAlign:'center'}, s.text);
    tl.fromTo(g, {opacity:0, rotation:left?-20:20, x:left?-80:80}, {opacity:1, rotation:0, x:0, duration:0.4, ease:'back.out(2)'}, at + 0.4 + i*0.3);
  });
  return {post};
};

/* 21. 대각선 점무늬 띠가 쓸고 지나가며 장면 전환. at 시각에 화면을 덮고 at+0.45 에 다 지나감 */
M.halftoneWipe = function(tl, at, o){
  const p = host(o);
  const w = el('div', 'm-wipe', p, {zIndex:50});
  tl.fromTo(w, {x:0}, {x:3200, duration:0.9, ease:'power2.inOut'}, at - 0.45);
  return {w};
};

/* 22. 배경에 큰 순위 숫자. opts: text, y */
M.bigBgNumber = function(tl, at, o){
  const p = host(o);
  const b = el('div', 'm-bignum', p, {top:(o.y||520)+'px', zIndex:0}, o.text);
  tl.fromTo(b, {opacity:0, scale:1.3}, {opacity:o.alpha||0.08, scale:1, duration:0.5, ease:'power3.out'}, at);
  if(o.until) tl.to(b, {opacity:0, duration:0.2}, o.until);
  return {b};
};

/* 23. 기기 프레임 바꾸기: 같은 내용을 모니터 → 레트로 TV 로. opts: text */
M.frameSwap = function(tl, at, o){
  const p = host(o);
  const mon = el('div', 'm-monitor', p, {left:'160px', top:'720px'}, `<div class="s">${o.text||'오늘의 도구'}</div>`);
  const tv = el('div', 'm-tv', p, {left:'180px', top:'690px', opacity:0}, `<div class="s">${o.text2||o.text||'오늘의 도구'}</div>`);
  tl.fromTo(mon, {opacity:0, y:80}, {opacity:1, y:0, duration:0.35, ease:'back.out(1.6)'}, at);
  tl.to(mon, {opacity:0, scale:0.85, duration:0.2}, at + 1.3);
  tl.fromTo(tv, {opacity:0, scale:1.2, rotation:4}, {opacity:1, scale:1, rotation:0, duration:0.35, ease:'back.out(2)'}, at + 1.4);
  return {mon, tv};
};

/* 장 전환 보조: 배경색 바꾸기. opts: el(배경 요소), color */
M.sectionColor = function(tl, at, o){
  const bg = o.el || document.getElementById('bgc');
  if(bg) tl.to(bg, {backgroundColor:o.color, duration:o.dur||0.35, ease:'power2.inOut'}, at);
};

window.M = M;
})();
