// setT(t): t초 순간의 화면을 그린다. 모든 상태는 t에서만 계산한다(프레임마다 결정적).
const N = C.items.length;
// 항목 길이는 고정하지 않는다. 마지막 움직임이 끝나고 HOLD초(읽을 시간)만 지나면 바로 다음 항목으로 넘어간다.
const T_HOOK = 4.0, HOLD = 1.3, SUM_HOLD = 2.0;
const $ = (s, r = document) => r.querySelector(s);
const cl = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const ease = x => 1 - Math.pow(1 - cl(x), 3);
const back = x => { x = cl(x); const c = 1.7; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
const ap = (t, t0, d = .3) => ease((t - t0) / d);

// ---------- 대화형 시간표 ----------
const CPS = .04, BAD_READ = 1.5;
function phase(ph, p0) {
  const n = ph.msg.reduce((a, s) => a + s[0].length, 0);
  const typeS = p0 + .15, typeE = typeS + n * CPS, sent = typeE + .2;
  const nh = ph.msg.filter(s => s[1]).length;
  const dots = sent + .35 + nh * .3, reply = dots + .6;
  return { n, typeS, typeE, sent, dots, reply, mark: reply + ph.reply.length * .38 + .2 };
}
function chatPlan(it) {
  const b = phase(it.bad, .4), clear = b.mark + BAD_READ, g = phase(it.good, clear + .4);
  return { b, g, clear, end: g.mark + .65 };
}
// ---------- 목록형 시간표 ----------
function listPlan(it) {
  const R = it.rows.length, step = Math.min(2.0, 8.4 / R);
  const rows = it.rows.map((_, j) => .9 + j * step);
  const lastOk = rows[R - 1] + .8;
  return { R, rows, lastOk, chip: lastOk + .35, cap2: rows[Math.floor(R / 2)] + .8, end: it.chip ? lastOk + .75 : lastOk + .3 };
}
const isChat = it => (it.type || "chat") === "chat";
const r1 = x => Math.round(x * 10) / 10;
const itemDur = it => r1((isChat(it) ? chatPlan(it) : listPlan(it)).end + HOLD);
const SUM_FOOT_END = 2.3 + C.summary.foot.length * .04;
const T_SUM = r1(Math.max(SUM_FOOT_END, 3.35) + SUM_HOLD);
const DURS = [T_HOOK, ...C.items.map(itemDur), T_SUM];
const STARTS = [0]; DURS.forEach((d, i) => STARTS.push(r1(STARTS[i] + d)));
const TOTAL = STARTS[N + 2];
// 슬라임이 반응할 순간(항목마다)
function beats(it) {
  const D = itemDur(it);
  if (isChat(it)) {
    const { b, g, clear } = chatPlan(it);
    return { moveA: g.dots - .3, moveB: g.reply + .5, big: [b.mark, g.mark],
      moods: [[b.mark, clear, "surprise"], [g.mark, D - .2, it.mood || "excited"]] };
  }
  const L = listPlan(it);
  return { moveA: L.cap2 - .6, moveB: L.cap2 + .8, big: [L.cap2, it.chip ? L.chip : L.lastOk],
    moods: [[it.chip ? L.chip : L.lastOk, D - .2, it.mood || "glint"]] };
}

function headAnim(sc, i, t) {
  const from = Math.max(0, i - 1), p = cl((t - .3) / .6);
  sc.querySelectorAll(".pg i").forEach((d, j) => d.className = (j < i || (j === i && t > .9)) ? "done" : "");
  $(".pg .fill", sc).style.width = (GAP * (from + (i - from) * ease(p))) + "px";
  const mini = $(".mini", sc);
  mini.style.left = (12 + GAP * (from + (i - from) * p) - 13) + "px";
  mini.style.top = (4 - Math.sin(Math.PI * p) * 30 * (i > 0 ? 1 : 0)) + "px";
  const tb = $(".ttl", sc), ta = ap(t, .15, .35);
  tb.style.opacity = ta; tb.style.transform = `translateX(${(1 - ta) * -40}px)`;
}
function typeHow(sc, text, t, t0) {
  $(".howt", sc).textContent = text.slice(0, Math.floor(cl((t - t0) / (text.length * .03)) * text.length));
}
function capSet(sc, html, a) { const c = $(".cap", sc); c.innerHTML = html; c.style.opacity = a; c.style.transform = `translateY(${(1 - a) * 20}px)`; }

function bubbleHTML(segs, sweepStart, t) {
  let j = 0;
  return segs.map(([s, hi]) => {
    if (!hi) return s;
    const p = cl((t - (sweepStart + j++ * .3)) / .3);
    return `<mark style="background-size:${p * 100}% 100%">${s}</mark>`;
  }).join("");
}

function drawChat(sc, it, t, card) {
  const { b: TB, g: TG, clear: CLEAR } = chatPlan(it);
  let shake = 0; const s0 = TB.mark;
  if (t > s0 && t < s0 + .4) shake = Math.sin((t - s0) * 45) * 12 * (1 - (t - s0) / .4);
  card.style.transform += ` translateX(${shake}px)`;
  const good = t >= CLEAR + .2, ph = good ? it.good : it.bad, P = good ? TG : TB;
  const pill = $(".pill", sc);
  pill.textContent = good ? (it.goodPill || "고쳐서") : (it.badPill || "보통은"); pill.className = "pill" + (good ? "" : " bad");
  const d = Math.abs(t - (CLEAR + .2)); pill.style.transform = `scaleY(${d < .18 ? d / .18 : 1})`;
  typeHow(sc, ph.how, t, good ? CLEAR + .2 : .3);
  const mb = $(".meter b", sc); let w = 0, col = "#E5484D";
  if (t >= TB.mark) w = 22 * ease((t - TB.mark) / .5);
  if (good && t >= TG.mark) { w = 22 + 70 * ease((t - TG.mark) / .7); col = "#3FC47A"; }
  mb.style.width = w + "%"; mb.style.background = col; $(".meter", sc).style.opacity = ap(t, .6, .3);
  const tx = $(".inp .tx", sc), send = $(".inp .send", sc);
  if (t < P.typeS || t >= P.sent) tx.innerHTML = `<span class=ph>${C.placeholder || "무엇이든 물어보세요"}</span>`;
  else { const k = Math.floor(cl((t - P.typeS) / (P.n * CPS)) * P.n); tx.innerHTML = ph.msg.map(s => s[0]).join("").slice(0, k) + "<span class=cur></span>"; }
  send.style.background = (t >= P.typeE - .05 && t < P.sent + .15) ? "#FF8A3D" : "#D9D3C7";
  send.style.transform = `scale(${t >= P.sent - .05 && t < P.sent + .15 ? .85 : 1})`;
  const me = $(".me", sc), ai = $(".ai", sc), dots = $(".dots", sc), stp = $(".stamp", sc), load = $(".load", sc);
  me.innerHTML = bubbleHTML(ph.msg, P.sent + .35, t);
  const fa = ap(t, P.sent, .3), out = good ? 0 : cl((t - CLEAR) / .35);
  me.style.opacity = Math.min(fa, 1 - out); me.style.transformOrigin = "100% 100%";
  me.style.transform = `translateY(${(1 - fa) * 380 - out * 90}px) scale(${.9 + .1 * fa})`;
  const meB = 88 + me.offsetHeight + 34;
  dots.style.top = (meB + 14) + "px"; dots.style.opacity = (t >= P.dots && t < P.reply) ? 1 : 0;
  dots.querySelectorAll("i").forEach((d, j) => d.style.transform = `translateY(${-Math.max(0, Math.sin(t * 7 - j * .9)) * 10}px)`);
  load.style.width = (t >= P.dots && t < P.reply + .15 ? cl((t - P.dots) / (P.reply - P.dots)) * 100 : 0) + "%";
  ai.style.top = meB + "px";
  let h = "";
  ph.reply.forEach((l, j) => { const a = ap(t, P.reply + j * .38, .25); if (a > 0) h += `<p style="opacity:${a};transform:translateX(${(1 - a) * -24}px)">${l}</p>`; });
  if (good) { const a = ap(t, P.mark, .25); if (a > 0) h += `<p class=chk style="opacity:${a}">✓ ${ph.check}</p><div class=chkbar style="width:${ease((t - P.mark - .15) / .5) * 100}%"></div>`; }
  ai.innerHTML = h; ai.style.opacity = 1 - out; ai.style.transform = `translateY(${-out * 90}px)`;
  if (!good) {
    const a = t >= P.mark ? back((t - P.mark) / .3) : 0;
    stp.textContent = ph.stamp; stp.style.top = (meB + 10) + "px";
    stp.style.opacity = Math.min(cl(a * 3), 1 - out); stp.style.transform = `translateY(${-out * 90}px) rotate(-8deg) scale(${2 - a})`;
  } else stp.style.opacity = 0;
  capSet(sc, ph.cap, good ? ap(t, TG.sent, .35) : ap(t, TB.mark, .35) * (1 - out));
}

function drawList(sc, it, t, card) {
  const L = listPlan(it);
  const pill = $(".pill", sc); pill.textContent = it.pill || "순서"; pill.className = "pill";
  typeHow(sc, it.how, t, .3);
  let done = 0;
  sc.querySelectorAll(".li").forEach((r, j) => {
    const a = ap(t, L.rows[j], .3);
    r.style.opacity = a; r.style.transform = `translateX(${(1 - a) * 60}px)`;
    $(".lb", r).style.width = ease((t - L.rows[j] - .2) / .6) * 100 + "%";
    const o = t >= L.rows[j] + .8 ? back((t - L.rows[j] - .8) / .3) : 0;
    $(".ok", r).style.opacity = cl(o * 3); $(".ok", r).style.transform = `scale(${o})`;
    if (t >= L.rows[j] + .8) done = j + 1;
    r.style.borderColor = (t >= L.rows[j] && t < L.rows[j] + 1.2) ? "#FF8A3D" : "#E2DED3";
  });
  const mb = $(".meter b", sc);
  mb.style.width = (done / L.R * 100) + "%"; mb.style.background = done === L.R ? "#3FC47A" : "#FF8A3D";
  $(".meter", sc).style.opacity = ap(t, .6, .3);
  $(".load", sc).style.width = ease((t - .9) / (L.lastOk - .9)) * 100 + "%";
  const chip = $(".chip", sc);
  if (chip) {
    const o = t >= L.chip ? back((t - L.chip) / .35) : 0;
    chip.style.opacity = cl(o * 3); chip.style.transform = `scale(${.6 + .4 * o}) rotate(${(1 - o) * -6}deg)`;
    if (t > L.chip && t < L.chip + .4) card.style.transform += ` translateX(${Math.sin((t - L.chip) * 45) * 8 * (1 - (t - L.chip) / .4)}px)`;
  }
  const caps = it.caps;
  if (t < L.cap2) capSet(sc, caps[0], ap(t, .5, .35) * (1 - cl((t - L.cap2 + .25) / .25)));
  else capSet(sc, caps[1], ap(t, L.cap2, .35));
}

function drawItem(i, t) {
  const sc = $("#s" + (i + 1)), it = C.items[i], card = $(".card", sc);
  const k = back(t / .45);
  card.style.transform = `translateY(${(1 - k) * 70}px) scale(${.96 + .04 * k})`;
  headAnim(sc, i, t);
  if (isChat(it)) drawChat(sc, it, t, card); else drawList(sc, it, t, card);
}

function drawHook(t) {
  const sc = $("#s0"), a = back((t - .05) / .35), tg = $(".tag", sc);
  tg.style.transform = `translateX(-50%) translateY(${(1 - a) * 30}px) scale(${.9 + .1 * a})`; tg.style.opacity = cl(a * 2);
  sc.querySelectorAll(".hl").forEach((l, k) => { const b = ap(t, .3 + k * .28, .3); l.style.opacity = b; l.style.transform = `translateY(${(1 - b) * 40}px)`; });
}

function drawSum(t) {
  const sc = $("#s" + (N + 1)), k = back(t / .45), R = C.summary.rows.length, step = 1.8 / R;
  $(".card", sc).style.transform = `translateY(${(1 - k) * 70}px)`;
  let done = 0;
  sc.querySelectorAll(".item").forEach((r, j) => {
    const s0 = .4 + j * step, a = ap(t, s0, .3);
    r.style.opacity = a; r.style.transform = `translateX(${(1 - a) * 40}px)`;
    // 체크 상자가 딸깍 채워지고 테두리 물결이 퍼진다
    const ck = t >= s0 + .45 ? back((t - s0 - .45) / .3) : 0, on = t >= s0 + .45;
    const u = $("u", r);
    u.style.background = on ? "#3FC47A" : "#1F141D"; u.style.borderColor = on ? "#3FC47A" : "#5A4256";
    u.style.transform = `scale(${on ? 1 + .18 * Math.sin(Math.PI * cl((t - s0 - .45) / .25)) : 1})`;
    $("b", u).style.transform = `scale(${ck})`; $("b", u).style.opacity = cl(ck * 3);
    const rp = cl((t - s0 - .45) / .5), em = $("em", u);
    em.style.opacity = on && rp < 1 ? (1 - rp) : 0; em.style.transform = `scale(${1 + rp * .9})`;
    const o = t >= s0 + .65 ? back((t - s0 - .65) / .3) : 0;
    $("s", r).style.opacity = cl(o * 3); $("s", r).style.transform = `scale(${o})`;
    if (t >= s0 + .65) done = j + 1;
  });
  $(".cnt", sc).textContent = done + " / " + R;
  sc.querySelectorAll(".segs i b").forEach((b, j) => {   // 한 칸씩 툭 튀어 오르며 찬다
    const s1 = .4 + j * step + .65, o = t >= s1 ? back((t - s1) / .3) : 0;
    b.style.transform = `scaleY(${o})`; b.style.background = done === R ? "#3FC47A" : "#FFCE54";
  });
  const ft = C.summary.foot, fk = Math.floor(cl((t - 2.3) / (ft.length * .04)) * ft.length);
  $(".foot", sc).textContent = ft.slice(0, fk) || " ";
  capSet(sc, C.summary.cap, ap(t, 3.0, .35));
}

// ---------- 슬라임: 장면을 넘나들며 이어서 움직인다 ----------
const HOP = .6, LX = 300, RX = 780, GROUND = 1560;
const KEYS = [[0, 540], [T_HOOK - .3, 540], [T_HOOK + .3, LX]];
const BIG = [1.4], MOODS = [[1.3, 3.6, C.hook.mood || "glint"]];
let side = LX;
C.items.forEach((it, i) => {
  const s = STARTS[i + 1], b = beats(it), o = side === LX ? RX : LX;
  KEYS.push([s + b.moveA, side], [s + b.moveB, o]);
  b.big.forEach(x => BIG.push(s + x));
  b.moods.forEach(([a, c, m]) => MOODS.push([s + a, s + c, m]));
  side = o;
});
const SE = STARTS[N + 1];
KEYS.push([SE + .2, side], [SE + 1.4, 540], [TOTAL + 1, 540]);
BIG.push(SE + 2.4, SE + 3.0); MOODS.push([SE + 2.4, TOTAL, "smile"]);
const SCALE = [[0, 1.45], [T_HOOK - .3, 1.45], [T_HOOK + .3, 1], [TOTAL + 1, 1]];
function lerpKeys(K, t) {
  for (let j = 0; j < K.length - 1; j++) { const [a, x0] = K[j], [b, x1] = K[j + 1]; if (t >= a && t <= b) return x0 + (x1 - x0) * (b > a ? (t - a) / (b - a) : 0); }
  return K[K.length - 1][1];
}
function drawSlime(t) {
  const n = Math.floor(t / HOP), ph = t / HOP - n;
  const xa = lerpKeys(KEYS, n * HOP), xb = lerpKeys(KEYS, (n + 1) * HOP);
  const air = cl((ph - .2) / .8), cx = xa + (xb - xa) * air;
  const big = BIG.some(b => b >= n * HOP && b < (n + 1) * HOP), moving = Math.abs(xb - xa) > 4;
  const H = big ? 55 : moving ? 40 : 18;
  const y = ph < .2 ? 0 : 4 * H * air * (1 - air);
  let sx, sy;
  if (ph < .2) { const q = Math.sin(Math.PI * ph / .2); sx = 1 + .18 * q * (H / 70); sy = 1 - .16 * q * (H / 70); }
  else { const v = Math.abs(1 - 2 * air); sx = 1 - .06 * v * (H / 70); sy = 1 + .08 * v * (H / 70); }
  sx = cl(sx, .8, 1.25); sy = cl(sy, .8, 1.2);
  const s = lerpKeys(SCALE, t) * .82, w = 256 * s, h = 224 * s;
  const mood = (MOODS.find(m => t >= m[0] && t <= m[1]) || [0, 0, "base"])[2];
  const sl = $("#sl"); if (sl.dataset.m !== mood) { sl.src = SPR[mood]; sl.dataset.m = mood; }
  sl.style.width = w + "px"; sl.style.height = h + "px";
  sl.style.left = (cx - w / 2) + "px"; sl.style.top = (GROUND - h - y) + "px";
  sl.style.transform = `scale(${sx},${sy})`;
  const shw = w * .8 * (1 - y / 400), sh = $("#sh");
  sh.style.width = shw + "px"; sh.style.left = (cx - shw / 2) + "px"; sh.style.top = (GROUND - 10) + "px"; sh.style.opacity = .9 - y / 300;
}

function setT(t) {
  for (let i = 0; i <= N + 1; i++) {
    const lt = t - STARTS[i], D = DURS[i], sc = $("#s" + i), last = i === N + 1;
    let o = 0;
    if (lt >= 0 && lt < D) o = Math.min(i === 0 ? 1 : cl(lt / .22), last ? 1 : cl((D - lt) / .22));
    if (last && lt >= D) o = 1;
    sc.style.opacity = o; sc.style.display = o > 0 ? "block" : "none";
    if (o > 0) { if (i === 0) drawHook(lt); else if (last) drawSum(lt); else drawItem(i - 1, lt); }
  }
  drawSlime(t);
}
window.TOTAL = TOTAL; window.STARTS = STARTS; window.DURS = DURS; window.setT = setT;
