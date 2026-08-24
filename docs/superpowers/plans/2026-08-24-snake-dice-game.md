# 뱀주사위놀이 (육성 버전) 구현 계획

> **For agentic workers:** 이 계획은 단일 파일 산출물이라 인라인 실행(superpowers:executing-plans)을 전제로 한다. 각 단계는 체크박스(`- [ ]`)로 추적한다.

**Goal:** 육성출판사 「뱀주사위놀이」를 사람 대 컴퓨터 턴제 웹 게임으로 만든다. 주사위 3D 애니메이션과 구분되는 두 말이 핵심이다.

**Architecture:** 외부 자산 없는 단일 `index.html`. 규칙은 DOM 을 모르는 순수 함수로 분리하고, 렌더링·애니메이션은 그 결과를 재생만 한다. 보드는 CSS 격자 위에 SVG 오버레이(뱀·고속도로)를 겹친다.

**Tech Stack:** HTML5 / CSS3 (3D transform, grid) / 바닐라 ES2020. 빌드 도구·프레임워크·외부 라이브러리 없음.

**Spec:** `docs/superpowers/specs/2026-08-24-snake-dice-game-design.md`

## Global Constraints

- 산출물은 `C:\Works\PROJECTS\SnakeGame\index.html` **한 파일**. CSS·JS 전부 인라인. 외부 요청(폰트 CDN 포함) 금지 — `file://` 더블클릭으로 완전히 동작해야 한다.
- `board.webp` 를 게임에서 사용하지 않는다. 참고용으로만 남긴다.
- 인코딩: UTF-8. `<meta charset="utf-8">` 필수. 문구는 한국어.
- 칸 번호는 1~100. 1번 좌하단, 100번 좌상단, 부스트로페돈.
- 고속도로 13개: `4→16, 8→12, 18→38, 20→74, 24→36, 32→56, 34→46, 40→60, 48→54, 70→88, 76→86, 80→100, 90→92`
- 뱀 12개: `22→2, 28→6, 30→10, 44→26, 58→42, 66→14, 68→52, 72→50, 84→62, 94→64, 96→82, 98→78`
- 규칙: 1번에서 시작 / 6은 재굴림(한 턴 3연속이면 종료) / 100 정확 도달, 초과분 되돌아옴 / 되돌아온 칸의 뱀·고속도로 발동 / 최종 칸에서 밀어내기(상대를 1번으로) / 연쇄 발동 없음
- 디버그 훅 `window.__forceDice` 를 남긴다.

---

### Task 1: 문서 골격과 보드 격자

**Files:**
- Create: `index.html`

**Interfaces:**
- Produces: `cellToXY(n) → {col, top}` — `col`·`top` 은 0~9 격자 인덱스(top 은 화면 위에서 0)
- Produces: DOM `#board`(격자 컨테이너), `.cell[data-n]` 100개

- [ ] **Step 1: `index.html` 뼈대 작성**

`<!doctype html>` + `<meta charset="utf-8">` + `<meta name="viewport" content="width=device-width,initial-scale=1">`.
`<style>` 와 `<script>` 를 인라인으로 둔다. 레이아웃은 `#app { display:flex }` — 좌측 `#boardWrap`, 우측 `#panel`.

- [ ] **Step 2: 좌표 함수 구현**

```js
// 칸 번호(1~100) → 격자 좌표. row 0 이 맨 아랫줄(1~10), 짝수 줄은 왼→오른쪽.
function cellToXY(n) {
  const i = n - 1;
  const row = Math.floor(i / 10);
  const col = (row % 2 === 0) ? (i % 10) : (9 - (i % 10));
  return { col, top: 9 - row };
}
```

- [ ] **Step 3: 격자 DOM 생성**

100번부터 1번까지 화면 순서대로 `.cell` 을 만든다. `cellToXY` 로 `grid-column`/`grid-row` 를 직접 지정하면 생성 순서와 무관하게 배치된다.

```js
const board = document.getElementById('board');
for (let n = 1; n <= 100; n++) {
  const { col, top } = cellToXY(n);
  const el = document.createElement('div');
  el.className = 'cell' + (((col + top) % 2) ? ' odd' : '');
  el.dataset.n = n;
  el.style.gridColumn = col + 1;
  el.style.gridRow = top + 1;
  el.innerHTML = `<span class="num">${n}</span>`;
  board.appendChild(el);
}
```

- [ ] **Step 4: 레트로 배색 CSS**

원본의 노란 바탕 + 체크무늬. `#board { display:grid; grid-template:repeat(10,1fr)/repeat(10,1fr); aspect-ratio:1; width:clamp(320px,52vmin,640px) }`.
`.cell` 기본 `#f7e96b`, `.cell.odd` `#fdf6b8`, 테두리 `1px solid #6b5b12`.

- [ ] **Step 5: 브라우저 확인**

`index.html` 을 띄워 1번이 좌하단, 10번이 우하단, 11번이 10번 바로 위(우측), 100번이 좌상단인지 눈으로 확인한다.

---

### Task 2: 보드 데이터와 SVG 오버레이

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes: `cellToXY(n)`
- Produces: `HIGHWAYS`(객체), `SNAKES`(객체), `STORIES`(객체 `{번호: 문구}`)
- Produces: `cellCenter(n) → {x, y}` — SVG viewBox(0~1000) 기준 칸 중심 좌표

- [ ] **Step 1: 데이터 상수 선언**

```js
const HIGHWAYS = {4:16, 8:12, 18:38, 20:74, 24:36, 32:56, 34:46,
                  40:60, 48:54, 70:88, 76:86, 80:100, 90:92};
const SNAKES   = {22:2, 28:6, 30:10, 44:26, 58:42, 66:14,
                  68:52, 72:50, 84:62, 94:64, 96:82, 98:78};
```

`STORIES` 는 스펙 3.2·3.3 표의 25개 문구를 시작 칸 번호를 키로 그대로 옮긴다.

- [ ] **Step 2: SVG 중심 좌표 함수**

```js
// viewBox 0 0 1000 1000 기준. 한 칸 = 100 x 100.
function cellCenter(n) {
  const { col, top } = cellToXY(n);
  return { x: col * 100 + 50, y: top * 100 + 50 };
}
```

- [ ] **Step 3: 고속도로 그리기**

`#overlay`(`<svg viewBox="0 0 1000 1000">`, `pointer-events:none`, 격자에 절대 겹침)에 그린다.
시작→도착 직선을 살짝 휘게 하려면 중점을 수직 방향으로 밀어 `Q` 곡선을 만든다.
같은 경로를 세 겹으로 겹쳐 리본 도로를 만든다:
1. 흰색 `stroke-width:26`, `stroke-linecap:round` — 도로 본체
2. 회색 `stroke-width:30` 을 그 아래 깔아 테두리
3. 노란 `stroke-width:3`, `stroke-dasharray:14 12` — 가운데 차선
도착점에 `<polygon>` 삼각형 화살표를 진행 방향 각도로 회전시켜 얹는다.

- [ ] **Step 4: 뱀 그리기**

시작(머리)→도착(꼬리) 사이를 물결지게 흔든 `path`. 두 점을 잇는 벡터에 수직으로 진폭을 번갈아 주는 제어점 3~4개로 `C`/`Q` 를 이어 붙인다.
몸통은 `stroke-linecap:round` 로 두 겹(어두운 초록 `stroke-width:22` 위에 밝은 초록 `stroke-width:14`).
머리는 시작 칸 중심에 타원 + 흰 눈 2개 + 빨간 혀(`<path>` 갈래).

- [ ] **Step 5: 셀 표식**

특수 칸의 `.cell` 에 `↗`(고속도로 시작) / `🐍`(뱀 시작) 배지를 우상단에 붙이고, 도착 칸에는 옅은 하이라이트 클래스를 준다.

- [ ] **Step 6: 브라우저 확인**

25개 경로가 모두 그려졌는지, 뱀 머리가 큰 번호(시작) 쪽에 있는지, 도로 화살표가 도착 칸을 가리키는지 확인한다.

---

### Task 3: 규칙 순수 함수

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes: `HIGHWAYS`, `SNAKES`
- Produces:
  ```
  resolveMove(from:number, dice:number) → {
    walkTo: number,          // 전진 후(바운스 전) 이론 위치, 최대 100 초과 가능
    bounced: boolean,
    landed: number,          // 바운스 반영, 뱀/고속도로 적용 전
    jump: 'highway'|'snake'|null,
    final: number,
    won: boolean
  }
  ```

- [ ] **Step 1: 구현**

```js
// 규칙 계층: DOM 을 모른다. 애니메이션은 이 결과를 재생만 한다.
function resolveMove(from, dice) {
  const walkTo = from + dice;
  const bounced = walkTo > 100;
  const landed = bounced ? 200 - walkTo : walkTo;   // 100 을 넘은 만큼 되돌아온다
  let jump = null;
  let final = landed;

  if (HIGHWAYS[landed] !== undefined) {
    jump = 'highway';
    final = HIGHWAYS[landed];
  } else if (SNAKES[landed] !== undefined) {
    jump = 'snake';
    final = SNAKES[landed];
  }

  return { walkTo, bounced, landed, jump, final, won: final === 100 };
}
```

- [ ] **Step 2: 콘솔로 경계값 확인**

브라우저 콘솔에서 아래를 실행해 결과를 눈으로 대조한다.

```js
resolveMove(97, 6)   // {landed:97, bounced:true, jump:null, final:97}
resolveMove(97, 3)   // {landed:100, jump:null, final:100, won:true}
resolveMove(74, 6)   // {landed:80, jump:'highway', final:100, won:true}
resolveMove(96, 6)   // walkTo 102 → landed 98 → 뱀 → final 78
resolveMove(1, 3)    // landed 4 → 고속도로 → final 16
```

`resolveMove(96,6)` 이 78 을 돌려주면 「되돌아온 칸의 뱀 발동」 규칙이 맞게 구현된 것이다.

---

### Task 4: 말 렌더링과 이동 애니메이션

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes: `cellToXY(n)`
- Produces: `PLAYERS` 배열 `[{id:'human', name:'나', icon:'🧑', pos:1, el}, {id:'cpu', ...}]`
- Produces: `placeToken(p, n, {instant})`, `async hopTo(p, to)`, `async slideTo(p, to)`

- [ ] **Step 1: 말 DOM 과 배치**

`#board` 안에 `.token` 두 개를 절대 배치한다. 칸 크기는 `board.clientWidth / 10` 로 계산하고 `transform: translate(x, y)` 로 옮긴다. 겹침 오프셋은 사람 `-22%`, 컴퓨터 `+22%`.

```js
function placeToken(p, n, opts = {}) {
  const { col, top } = cellToXY(n);
  const s = board.clientWidth / 10;
  const dx = (p.id === 'human' ? -0.16 : 0.16) * s;
  p.el.style.transition = opts.instant ? 'none' : '';
  p.el.style.transform = `translate(${col * s + s / 2 + dx}px, ${top * s + s / 2}px)`;
}
```

- [ ] **Step 2: 스타일**

사람: 배경 `#2b6cff`, 흰 실선 테두리 3px. 컴퓨터: 배경 `#e2382d`, 흰 이중 테두리(`border-style:double`, 5px). 둘 다 원형, `box-shadow` 로 바닥 그림자, 안에 이모지.
색 하나에 의존하지 않도록 아이콘과 테두리 모양을 함께 다르게 둔다.

- [ ] **Step 3: 한 칸씩 뛰는 이동**

```js
const sleep = ms => new Promise(r => setTimeout(r, ms));

// 한 칸씩 폴짝. from < to 면 전진, 아니면 후진.
async function hopTo(p, to) {
  const step = to > p.pos ? 1 : -1;
  while (p.pos !== to) {
    p.pos += step;
    p.el.classList.add('hop');
    placeToken(p, p.pos);
    await sleep(180);
    p.el.classList.remove('hop');
  }
}
```

`.hop` 은 `@keyframes` 로 살짝 떴다 내려앉는 180ms 애니메이션.

- [ ] **Step 4: 뱀/고속도로 미끄러짐**

```js
// 곡선을 타는 느낌. 한 칸씩 걷지 않고 700ms 동안 한 번에 옮긴다.
async function slideTo(p, to, kind) {
  p.el.classList.add(kind === 'snake' ? 'slide-snake' : 'slide-road');
  p.el.style.transition = 'transform 700ms cubic-bezier(.5,-0.2,.4,1.2)';
  p.pos = to;
  placeToken(p, to);
  await sleep(720);
  p.el.style.transition = '';
  p.el.classList.remove('slide-snake', 'slide-road');
}
```

- [ ] **Step 5: 리사이즈 대응**

`window.addEventListener('resize', () => PLAYERS.forEach(p => placeToken(p, p.pos, {instant:true})))`.

- [ ] **Step 6: 브라우저 확인**

콘솔에서 `hopTo(PLAYERS[0], 20)` 을 불러 말이 칸을 따라 뛰어가는지, 창 크기를 바꿔도 말이 칸 중앙에 남는지 확인한다.

---

### Task 5: 3D 주사위

**Files:**
- Modify: `index.html`

**Interfaces:**
- Produces: `async rollDice() → number` (1~6). `window.__forceDice` 가 설정돼 있으면 그 값을 쓴다.

- [ ] **Step 1: 큐브 마크업**

```html
<div class="dice-stage"><div class="dice" id="dice">
  <div class="face f1"></div><div class="face f2"></div><div class="face f3"></div>
  <div class="face f4"></div><div class="face f5"></div><div class="face f6"></div>
</div></div>
```

각 면은 `translateZ(32px)` + 축 회전으로 정육면체를 만들고, pip 은 CSS grid 로 배치한다(1·3·5는 가운데 pip 포함).

- [ ] **Step 2: 값 → 최종 회전각 표**

```js
// 각 눈이 정면(카메라 쪽)에 오도록 하는 회전각.
const FACE_ROT = {
  1: [  0,   0], 2: [  0, -90], 3: [  0, 180],
  4: [  0,  90], 5: [-90,   0], 6: [ 90,   0]
};
```

- [ ] **Step 3: 굴리기**

```js
async function rollDice() {
  const value = window.__forceDice ?? (1 + Math.floor(Math.random() * 6));
  const [rx, ry] = FACE_ROT[value];
  // 여러 바퀴 더 돌린 뒤 목표 각도에 착지시킨다. 결과는 시작 시점에 이미 확정됐다.
  const spins = 3 + Math.floor(Math.random() * 2);
  dice.style.transition = 'transform 900ms cubic-bezier(.2,.9,.2,1)';
  dice.style.transform =
    `rotateX(${rx + 360 * spins}deg) rotateY(${ry + 360 * spins}deg)`;
  await sleep(900);
  // 다음 굴림이 항상 앞으로 돌도록 각도를 정규화한다.
  dice.style.transition = 'none';
  dice.style.transform = `rotateX(${rx}deg) rotateY(${ry}deg)`;
  dice.classList.add('landed');
  await sleep(220);
  dice.classList.remove('landed');
  return value;
}
```

`.landed` 는 스케일 펄스 + 글로우 200ms.

- [ ] **Step 4: 브라우저 확인**

콘솔에서 `for (let i=1;i<=6;i++) { window.__forceDice=i; await rollDice(); }` 를 돌려 **표시된 눈이 반환값과 일치**하는지 6번 모두 확인한다. 어긋나면 `FACE_ROT` 표와 면 배치가 안 맞는 것이므로 표를 고친다. 확인 후 `window.__forceDice = null`.

---

### Task 6: 턴 상태머신과 패널

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes: `resolveMove`, `rollDice`, `hopTo`, `slideTo`, `placeToken`, `STORIES`
- Produces: `async takeTurn()`, `log(msg, who)`, `showStory(n, kind)`

- [ ] **Step 1: 사이드 패널 마크업**

플레이어 카드 2장(아이콘·이름·「현재 N칸」·`.active` 턴 표시) → 주사위 스테이지 → `#rollBtn` → `#log`(최근 순, `max-height` + `overflow:auto`).

- [ ] **Step 2: 교훈 카드**

`showStory(n, kind)` 는 화면 중앙에 오버레이 카드를 띄운다. 고속도로는 파란 테두리 + `↗`, 뱀은 초록 테두리 + `🐍`. 문구는 `STORIES[n]`, 아래에 `N번 → M번` 을 적는다. 페이드인 300ms → 유지 1200ms → 페이드아웃 300ms.

- [ ] **Step 3: 턴 진행**

```js
let sixStreak = 0;
let busy = false;

async function takeTurn() {
  if (busy || state.over) return;
  busy = true;
  setRollEnabled(false);

  const p = PLAYERS[state.turn];
  const dice = await rollDice();
  log(`${p.name} · 주사위 ${dice}`, p.id);

  const r = resolveMove(p.pos, dice);

  if (r.bounced) {
    await hopTo(p, 100);                 // 100 을 찍고
    log('100을 넘어 되돌아온다', p.id);
    await hopTo(p, r.landed);            // 초과분만큼 되돌아온다
  } else {
    await hopTo(p, r.landed);
  }

  if (r.jump) {
    showStory(r.landed, r.jump);
    await sleep(700);
    await slideTo(p, r.final, r.jump);
    log(`${r.landed} → ${r.final} (${r.jump === 'snake' ? '뱀' : '고속도로'})`, p.id);
  }

  // 밀어내기: 뱀/고속도로까지 끝난 최종 칸에서만 판정한다.
  const other = PLAYERS[1 - state.turn];
  if (!r.won && other.pos === p.pos && p.pos !== 1) {
    await hopTo(other, 1);
    log(`${other.name}의 말이 1번으로 밀려났다`, p.id);
  }

  updatePanel();

  if (r.won) {
    state.over = true;
    showWinner(p);
    busy = false;
    return;
  }

  sixStreak = (dice === 6) ? sixStreak + 1 : 0;
  const again = (dice === 6 && sixStreak < 3);
  if (!again) {
    sixStreak = 0;
    state.turn = 1 - state.turn;
  } else {
    log('6! 한 번 더', p.id);
  }

  busy = false;
  nextStep();
}
```

- [ ] **Step 4: 턴 디스패치**

```js
function nextStep() {
  updatePanel();
  if (state.over) return;
  if (PLAYERS[state.turn].id === 'cpu') {
    setRollEnabled(false);
    setTimeout(takeTurn, 800);           // 컴퓨터는 뜸을 들이고 자동으로 굴린다
  } else {
    setRollEnabled(true);
  }
}
```

- [ ] **Step 5: 브라우저 확인**

한 판을 끝까지 진행해 턴이 정상적으로 넘어가는지, 컴퓨터 턴에 버튼이 잠기는지, 로그가 쌓이는지 확인한다.

---

### Task 7: 승리 처리·반응형·최종 검증

**Files:**
- Modify: `index.html`

- [ ] **Step 1: 승자 오버레이**

`#winner` 전체 화면 오버레이 — 승자 아이콘·이름·「승리!」 + `#againBtn`(다시 하기). 다시 하기는 두 말을 1번으로, 로그를 비우고, `state` 를 초기화한 뒤 사람 턴부터 시작한다.

- [ ] **Step 2: 반응형**

`@media (max-width: 900px)` 에서 `#app { flex-direction: column }`, 보드 `width: min(94vw, 520px)`. 패널은 가로로 눕혀 카드 2장을 나란히 둔다.

- [ ] **Step 3: 스펙 6절 경계값 실측**

`window.__forceDice` 로 아래를 각각 재현해 확인한다.

| 확인 | 방법 | 기대 |
|---|---|---|
| 정확 도달 | 97에서 `__forceDice=6` | 100 찍고 97로 되돌아옴 |
| 되돌아온 칸의 뱀 | 96에서 `__forceDice=6` | 98 뱀 → 78 |
| 즉시 승리 | 74에서 `__forceDice=6` | 80 고속도로 → 100 승리 |
| 6 재굴림 | `__forceDice=6` 고정 | 3연속 후 턴이 넘어감 |
| 밀어내기 | 두 말을 같은 칸으로 유도 | 상대가 1번으로 |
| 반응형 | 창 폭을 좁힘 | 보드가 깨지지 않고 말이 칸 중앙 유지 |

- [ ] **Step 4: 콘솔 에러 확인**

한 판 진행하는 동안 콘솔에 에러·경고가 없는지 확인한다.

---

## Self-Review 결과

- **스펙 커버리지**: 3.1 좌표 → Task 1 / 3.2·3.3 데이터·문구 → Task 2 / 4장 규칙 → Task 3·6 / 5.2 렌더링 → Task 1·2·4 / 5.3 애니메이션 → Task 4·5 / 5.4 상태머신 → Task 6 / 5.5 배치 → Task 6·7 / 5.6 말 구분 → Task 4 / 6장 검증 → Task 7. 누락 없음.
- **타입 일관성**: `resolveMove` 반환 필드(`walkTo/bounced/landed/jump/final/won`)를 Task 6 에서 그대로 쓴다. `cellToXY` 는 `{col, top}` 로 Task 1·2·4 에서 일관된다.
- **미해결**: 없음.
