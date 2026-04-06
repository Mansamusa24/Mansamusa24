// ─── Horse Riding Game ───────────────────────────────────────────────────────
// Controls: Space / Up Arrow = Jump, Down Arrow = Duck
// Avoid: logs (ground), branches (air)  |  Collect: coins (+10 pts)

const canvas  = document.getElementById('gameCanvas');
const ctx     = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;

// ── Palette ──────────────────────────────────────────────────────────────────
const SKY_TOP    = '#87ceeb';
const SKY_BOT    = '#d4f0ff';
const GROUND_COL = '#5c8a3c';
const DIRT_COL   = '#8b6914';
const SUN_COL    = '#ffe066';

// ── Constants ────────────────────────────────────────────────────────────────
const GROUND_Y   = H - 80;          // top of ground strip
const HORSE_X    = 120;
const GRAVITY    = 0.55;
const JUMP_VEL   = -13;
const DUCK_H     = 28;              // horse height when ducking
const STAND_H    = 60;              // horse normal height
const HORSE_W    = 72;

// ── State ────────────────────────────────────────────────────────────────────
let state        = 'idle';          // idle | running | dead
let score        = 0;
let lives        = 3;
let distance     = 0;
let speed        = 4;               // pixels per frame
let frameCount   = 0;

// Horse
const horse = {
  x: HORSE_X,
  y: GROUND_Y - STAND_H,
  vy: 0,
  h: STAND_H,
  ducking: false,
  jumping: false,
  frame: 0,      // animation frame
  frameTick: 0,
};

// Scrolling background layers
const clouds  = [];
const hills   = [];
let bgX = 0;

// Obstacles & coins
let obstacles = [];
let coins     = [];

// Input
const keys = {};
document.addEventListener('keydown', e => {
  keys[e.code] = true;
  if ((e.code === 'Space' || e.code === 'ArrowUp') && state === 'running') {
    doJump();
    e.preventDefault();
  }
  if (e.code === 'ArrowDown') e.preventDefault();
});
document.addEventListener('keyup', e => { keys[e.code] = false; });

// Touch support
canvas.addEventListener('touchstart', e => {
  if (state === 'running') doJump();
  e.preventDefault();
}, { passive: false });

document.getElementById('startBtn').addEventListener('click', startGame);

// ── Init helpers ─────────────────────────────────────────────────────────────
function initBackground() {
  clouds.length = 0;
  for (let i = 0; i < 5; i++) {
    clouds.push({ x: Math.random() * W, y: 30 + Math.random() * 80, w: 60 + Math.random() * 80 });
  }
  hills.length = 0;
  for (let i = 0; i < 4; i++) {
    hills.push({ x: i * 220, r: 100 + Math.random() * 60 });
  }
}

function resetGame() {
  score = 0; lives = 3; distance = 0; speed = 4; frameCount = 0;
  horse.y = GROUND_Y - STAND_H;
  horse.vy = 0; horse.h = STAND_H; horse.ducking = false; horse.jumping = false;
  obstacles.length = 0; coins.length = 0;
  updateUI();
  initBackground();
}

function startGame() {
  document.getElementById('overlay').style.display = 'none';
  resetGame();
  state = 'running';
  requestAnimationFrame(loop);
}

// ── Jump / Duck ───────────────────────────────────────────────────────────────
function doJump() {
  if (!horse.jumping) {
    horse.vy = JUMP_VEL;
    horse.jumping = true;
  }
}

// ── Spawning ─────────────────────────────────────────────────────────────────
const MIN_GAP = 280;
let lastObstacleX = W;

function spawnObstacle() {
  if (obstacles.length > 0) {
    const last = obstacles[obstacles.length - 1];
    if (last.x > W - MIN_GAP) return;
  }
  if (Math.random() < 0.015) {
    const type = Math.random() < 0.5 ? 'log' : 'branch';
    obstacles.push(type === 'log'
      ? { type: 'log',    x: W, y: GROUND_Y - 32, w: 28, h: 32 }
      : { type: 'branch', x: W, y: GROUND_Y - STAND_H - 10, w: 60, h: 18 }
    );
  }
}

function spawnCoin() {
  if (Math.random() < 0.008) {
    const y = GROUND_Y - STAND_H - 20 - Math.random() * 30;
    coins.push({ x: W, y, r: 10, collected: false });
  }
}

// ── Collision (AABB) ──────────────────────────────────────────────────────────
function horseRect() {
  return {
    x: horse.x + 10,
    y: horse.y + (horse.ducking ? STAND_H - DUCK_H : 0),
    w: HORSE_W - 20,
    h: horse.h,
  };
}

function aabb(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x &&
         a.y < b.y + b.h && a.y + a.h > b.y;
}

// ── UI ────────────────────────────────────────────────────────────────────────
function updateUI() {
  document.getElementById('score').textContent = score;
  document.getElementById('lives').textContent = '♥'.repeat(lives);
  document.getElementById('speed').textContent = speed.toFixed(1) + 'x';
}

// ── Drawing helpers ───────────────────────────────────────────────────────────
function drawSky() {
  const grad = ctx.createLinearGradient(0, 0, 0, GROUND_Y);
  grad.addColorStop(0, SKY_TOP);
  grad.addColorStop(1, SKY_BOT);
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, W, GROUND_Y);
}

function drawSun() {
  ctx.fillStyle = SUN_COL;
  ctx.beginPath();
  ctx.arc(W - 70, 55, 28, 0, Math.PI * 2);
  ctx.fill();
  // rays
  ctx.strokeStyle = SUN_COL;
  ctx.lineWidth = 3;
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2;
    ctx.beginPath();
    ctx.moveTo(W - 70 + Math.cos(a) * 33, 55 + Math.sin(a) * 33);
    ctx.lineTo(W - 70 + Math.cos(a) * 42, 55 + Math.sin(a) * 42);
    ctx.stroke();
  }
}

function drawClouds() {
  ctx.fillStyle = 'rgba(255,255,255,0.85)';
  for (const c of clouds) {
    drawCloud(c.x, c.y, c.w);
  }
}

function drawCloud(x, y, w) {
  const h = w * 0.4;
  ctx.beginPath();
  ctx.ellipse(x,       y,       w * 0.5, h * 0.6, 0, 0, Math.PI * 2);
  ctx.ellipse(x - w * 0.25, y + h * 0.2, w * 0.35, h * 0.5, 0, 0, Math.PI * 2);
  ctx.ellipse(x + w * 0.25, y + h * 0.2, w * 0.35, h * 0.5, 0, 0, Math.PI * 2);
  ctx.fill();
}

function drawHills() {
  ctx.fillStyle = '#7ab648';
  for (const h of hills) {
    ctx.beginPath();
    ctx.arc(h.x, GROUND_Y, h.r, Math.PI, 0);
    ctx.fill();
  }
}

function drawGround() {
  // Grass strip
  ctx.fillStyle = GROUND_COL;
  ctx.fillRect(0, GROUND_Y, W, 20);
  // Dirt
  ctx.fillStyle = DIRT_COL;
  ctx.fillRect(0, GROUND_Y + 20, W, H - GROUND_Y - 20);
  // scrolling pebbles / grass tufts
  ctx.fillStyle = '#4a7a30';
  for (let i = 0; i < 10; i++) {
    const px = ((i * 90 - bgX * 0.8) % W + W) % W;
    ctx.fillRect(px, GROUND_Y + 4, 6, 10);
  }
}

// ── Horse drawing ─────────────────────────────────────────────────────────────
function drawHorse() {
  const hx = horse.x;
  const hy = horse.y;
  const ducking = horse.ducking;
  const t = horse.frame;  // animation frame 0-3

  // Leg animation offsets (gallop cycle)
  const legCycle = [0, 10, 0, -10];
  const lf = legCycle[t % 4];

  ctx.save();

  if (ducking) {
    // Ducking — body is lower/squished
    drawHorseBody(hx, hy + 32, 1, 0.55);
  } else {
    drawHorseBody(hx, hy, 1, 1, lf);
  }

  ctx.restore();
}

function drawHorseBody(hx, hy, sx, sy, legOffset = 0) {
  ctx.save();
  ctx.translate(hx, hy);
  ctx.scale(sx, sy);

  const body_color = '#8B6914';
  const dark_color = '#5c4a0a';
  const mane_color = '#3a2800';

  // Body
  ctx.fillStyle = body_color;
  ctx.beginPath();
  ctx.ellipse(36, 38, 28, 20, 0, 0, Math.PI * 2);
  ctx.fill();

  // Neck
  ctx.fillStyle = body_color;
  ctx.beginPath();
  ctx.moveTo(52, 24);
  ctx.lineTo(62, 10);
  ctx.lineTo(68, 14);
  ctx.lineTo(58, 34);
  ctx.closePath();
  ctx.fill();

  // Head
  ctx.fillStyle = body_color;
  ctx.beginPath();
  ctx.ellipse(66, 10, 12, 9, -0.3, 0, Math.PI * 2);
  ctx.fill();

  // Snout
  ctx.fillStyle = '#a07828';
  ctx.beginPath();
  ctx.ellipse(75, 13, 6, 5, 0.2, 0, Math.PI * 2);
  ctx.fill();

  // Nostril
  ctx.fillStyle = dark_color;
  ctx.beginPath();
  ctx.ellipse(77, 14, 2, 1.5, 0, 0, Math.PI * 2);
  ctx.fill();

  // Eye
  ctx.fillStyle = '#222';
  ctx.beginPath();
  ctx.arc(66, 7, 2.5, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#fff';
  ctx.beginPath();
  ctx.arc(67, 6.5, 1, 0, Math.PI * 2);
  ctx.fill();

  // Ear
  ctx.fillStyle = body_color;
  ctx.beginPath();
  ctx.moveTo(60, 3); ctx.lineTo(56, -5); ctx.lineTo(64, 1);
  ctx.closePath();
  ctx.fill();

  // Mane
  ctx.fillStyle = mane_color;
  ctx.beginPath();
  ctx.moveTo(62, 3);
  ctx.bezierCurveTo(58, 10, 54, 18, 52, 24);
  ctx.lineTo(56, 25);
  ctx.bezierCurveTo(58, 18, 62, 12, 65, 5);
  ctx.closePath();
  ctx.fill();

  // Tail
  ctx.strokeStyle = mane_color;
  ctx.lineWidth = 5;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(8, 30);
  ctx.bezierCurveTo(-10, 40 + legOffset * 0.5, -8, 55, 0, 62);
  ctx.stroke();
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(8, 30);
  ctx.bezierCurveTo(-12, 35, -5, 58, 3, 65);
  ctx.stroke();

  // Legs (4 legs with gallop animation)
  ctx.strokeStyle = body_color;
  ctx.lineWidth = 7;
  ctx.lineCap = 'round';

  const legs = [
    { x: 22, swing: -legOffset },      // back-left
    { x: 30, swing:  legOffset },      // back-right
    { x: 46, swing:  legOffset },      // front-left
    { x: 54, swing: -legOffset },      // front-right
  ];

  for (const leg of legs) {
    ctx.beginPath();
    ctx.moveTo(leg.x, 52);
    ctx.lineTo(leg.x + leg.swing * 0.4, 62);
    ctx.lineTo(leg.x + leg.swing * 0.6, 72);
    ctx.stroke();

    // Hoof
    ctx.fillStyle = dark_color;
    ctx.beginPath();
    ctx.ellipse(leg.x + leg.swing * 0.6, 74, 5, 3, 0, 0, Math.PI * 2);
    ctx.fill();
  }

  // Saddle
  ctx.fillStyle = '#8b3a3a';
  ctx.beginPath();
  ctx.ellipse(38, 24, 14, 6, -0.1, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#a04040';
  ctx.beginPath();
  ctx.ellipse(38, 22, 10, 4, -0.1, 0, Math.PI * 2);
  ctx.fill();

  ctx.restore();
}

// ── Obstacle drawing ──────────────────────────────────────────────────────────
function drawObstacles() {
  for (const o of obstacles) {
    if (o.type === 'log') {
      // Wooden log
      ctx.fillStyle = '#8b5e3c';
      ctx.beginPath();
      ctx.roundRect(o.x, o.y, o.w, o.h, 4);
      ctx.fill();
      ctx.strokeStyle = '#5c3a1a';
      ctx.lineWidth = 2;
      ctx.stroke();
      // Wood grain lines
      ctx.strokeStyle = '#a0723a';
      ctx.lineWidth = 1;
      for (let i = 6; i < o.h; i += 6) {
        ctx.beginPath();
        ctx.moveTo(o.x + 3, o.y + i);
        ctx.lineTo(o.x + o.w - 3, o.y + i);
        ctx.stroke();
      }
      // End rings
      ctx.fillStyle = '#6b4820';
      ctx.beginPath();
      ctx.ellipse(o.x + o.w / 2, o.y + o.h / 2, o.w / 2 - 1, o.h / 2 - 1, 0, 0, Math.PI * 2);
      ctx.fill();
    } else {
      // Branch (diagonal obstacle at head height)
      ctx.strokeStyle = '#5c3a1a';
      ctx.lineWidth = o.h;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(o.x, o.y + o.h / 2 - 5);
      ctx.lineTo(o.x + o.w, o.y + o.h / 2 + 5);
      ctx.stroke();
      // Leaves
      ctx.fillStyle = '#3a7a20';
      for (let i = 0; i < 5; i++) {
        const lx = o.x + i * (o.w / 4);
        const ly = o.y + o.h / 2 - 8 + (i % 2) * -6;
        ctx.beginPath();
        ctx.ellipse(lx, ly, 10, 6, Math.random() * 0.5, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }
}

// ── Coin drawing ──────────────────────────────────────────────────────────────
function drawCoins() {
  for (const c of coins) {
    if (c.collected) continue;
    const bob = Math.sin(frameCount * 0.08 + c.x * 0.02) * 3;
    ctx.save();
    ctx.translate(c.x, c.y + bob);

    // Outer ring
    ctx.fillStyle = '#f0c040';
    ctx.beginPath();
    ctx.arc(0, 0, c.r, 0, Math.PI * 2);
    ctx.fill();

    // Shine
    ctx.fillStyle = '#ffe080';
    ctx.beginPath();
    ctx.arc(-2, -2, c.r * 0.45, 0, Math.PI * 2);
    ctx.fill();

    // $ symbol
    ctx.fillStyle = '#b08000';
    ctx.font = `bold ${c.r}px serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('$', 0, 1);

    ctx.restore();
  }
}

// ── Score popup particles ─────────────────────────────────────────────────────
const particles = [];

function spawnScoreParticle(x, y, text) {
  particles.push({ x, y, text, life: 60, vy: -1.5 });
}

function updateParticles() {
  for (const p of particles) {
    p.y += p.vy;
    p.life--;
  }
  // remove dead
  for (let i = particles.length - 1; i >= 0; i--) {
    if (particles[i].life <= 0) particles.splice(i, 1);
  }
}

function drawParticles() {
  for (const p of particles) {
    ctx.save();
    ctx.globalAlpha = p.life / 60;
    ctx.fillStyle = '#f0d080';
    ctx.font = 'bold 18px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(p.text, p.x, p.y);
    ctx.restore();
  }
}

// ── HUD ───────────────────────────────────────────────────────────────────────
function drawHUD() {
  // Distance ribbon
  ctx.fillStyle = 'rgba(0,0,0,0.35)';
  ctx.beginPath();
  ctx.roundRect(10, 10, 160, 32, 6);
  ctx.fill();
  ctx.fillStyle = '#f0d080';
  ctx.font = 'bold 16px sans-serif';
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  ctx.fillText(`🏇 ${Math.floor(distance)}m`, 20, 26);
}

// ── Flash effect when hit ─────────────────────────────────────────────────────
let flashFrames = 0;

function triggerFlash() { flashFrames = 20; }

function drawFlash() {
  if (flashFrames > 0) {
    ctx.fillStyle = `rgba(255,80,80,${flashFrames / 40})`;
    ctx.fillRect(0, 0, W, H);
    flashFrames--;
  }
}

// ── Invincibility after hit ───────────────────────────────────────────────────
let invincible = 0;   // frames of invincibility remaining

// ── Game over overlay ─────────────────────────────────────────────────────────
function showGameOver() {
  const overlay = document.getElementById('overlay');
  overlay.innerHTML = `
    <h1>Game Over</h1>
    <p>Distance: <b>${Math.floor(distance)}m</b><br>Score: <b>${score}</b></p>
    <button id="startBtn">Ride Again!</button>
  `;
  overlay.style.display = 'block';
  document.getElementById('startBtn').addEventListener('click', startGame);
}

// ── Main update ───────────────────────────────────────────────────────────────
function update() {
  frameCount++;
  distance += speed * 0.05;

  // Speed ramp-up every 500m
  speed = 4 + Math.floor(distance / 500) * 0.5;
  speed = Math.min(speed, 12);

  // ── Horse physics ──
  horse.ducking = !horse.jumping && !!keys['ArrowDown'];
  horse.h = horse.ducking ? DUCK_H : STAND_H;

  horse.vy += GRAVITY;
  horse.y  += horse.vy;

  const groundPos = GROUND_Y - horse.h;
  if (horse.y >= groundPos) {
    horse.y = groundPos;
    horse.vy = 0;
    horse.jumping = false;
  }

  // Gallop animation (faster when more speed)
  horse.frameTick++;
  const animRate = Math.max(4, 10 - Math.floor(speed));
  if (horse.frameTick >= animRate) {
    horse.frameTick = 0;
    horse.frame = (horse.frame + 1) % 4;
  }

  // ── Clouds scrolling ──
  for (const c of clouds) {
    c.x -= speed * 0.15;
    if (c.x + c.w < 0) {
      c.x = W + c.w;
      c.y = 30 + Math.random() * 80;
      c.w = 60 + Math.random() * 80;
    }
  }

  // ── Hills scrolling ──
  for (const h of hills) {
    h.x -= speed * 0.4;
    if (h.x + h.r < 0) h.x = W + h.r;
  }

  bgX += speed;

  // ── Obstacles ──
  spawnObstacle();
  for (let i = obstacles.length - 1; i >= 0; i--) {
    obstacles[i].x -= speed;
    if (obstacles[i].x + obstacles[i].w < 0) {
      obstacles.splice(i, 1);
      score += 5;           // survived an obstacle
      updateUI();
    }
  }

  // ── Coins ──
  spawnCoin();
  for (let i = coins.length - 1; i >= 0; i--) {
    coins[i].x -= speed;
    if (coins[i].x + coins[i].r < 0) {
      coins.splice(i, 1);
      continue;
    }
    // Collect
    if (!coins[i].collected) {
      const hr = horseRect();
      const cr = { x: coins[i].x - coins[i].r, y: coins[i].y - coins[i].r,
                   w: coins[i].r * 2,           h: coins[i].r * 2 };
      if (aabb(hr, cr)) {
        coins[i].collected = true;
        score += 10;
        spawnScoreParticle(coins[i].x, coins[i].y, '+10');
        coins.splice(i, 1);
        updateUI();
      }
    }
  }

  // ── Collision with obstacles ──
  if (invincible === 0) {
    const hr = horseRect();
    for (let i = obstacles.length - 1; i >= 0; i--) {
      if (aabb(hr, obstacles[i])) {
        lives--;
        updateUI();
        triggerFlash();
        invincible = 90;  // ~1.5s invincible
        obstacles.splice(i, 1);
        if (lives <= 0) {
          state = 'dead';
          showGameOver();
          return;
        }
        break;
      }
    }
  } else {
    invincible--;
  }

  updateParticles();
}

// ── Main draw ─────────────────────────────────────────────────────────────────
function draw() {
  ctx.clearRect(0, 0, W, H);

  drawSky();
  drawSun();
  drawClouds();
  drawHills();
  drawGround();
  drawCoins();
  drawObstacles();

  // Blink horse while invincible
  if (invincible === 0 || Math.floor(invincible / 6) % 2 === 0) {
    drawHorse();
  }

  drawFlash();
  drawParticles();
  drawHUD();
}

// ── Game loop ─────────────────────────────────────────────────────────────────
function loop() {
  if (state !== 'running') return;
  update();
  draw();
  requestAnimationFrame(loop);
}
