'use strict';
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const VIDEO_DIR = path.join(__dirname, 'output');
const OUTPUT_NAME = 'claude-code-batch-articles.mp4';
const W = 1080, H = 1920;

// ── Overlay helpers ──────────────────────────────────────────────

async function injectCursor(page) {
  await page.evaluate(() => {
    if (document.getElementById('demo-cursor')) return;
    const c = document.createElement('div');
    c.id = 'demo-cursor';
    c.innerHTML = `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M5 3L19 12L12 13L9 20L5 3Z" fill="white" stroke="black" stroke-width="1.5" stroke-linejoin="round"/>
    </svg>`;
    c.style.cssText = 'position:fixed;z-index:999999;pointer-events:none;width:28px;height:28px;transition:left 0.08s,top 0.08s;filter:drop-shadow(1px 1px 3px rgba(0,0,0,0.5));';
    c.style.left = '100px'; c.style.top = '200px';
    document.body.appendChild(c);
    document.addEventListener('mousemove', e => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; });
  });
}

async function injectSubtitleBar(page) {
  await page.evaluate(() => {
    if (document.getElementById('demo-subtitle')) return;
    const bar = document.createElement('div');
    bar.id = 'demo-subtitle';
    bar.style.cssText = 'position:fixed;bottom:60px;left:40px;right:40px;z-index:999998;text-align:center;padding:16px 28px;background:rgba(0,0,0,0.82);color:white;font-family:-apple-system,"Microsoft YaHei","PingFang SC",sans-serif;font-size:32px;font-weight:700;letter-spacing:1px;border-radius:12px;transition:opacity 0.35s;pointer-events:none;line-height:1.4;';
    bar.textContent = '';
    bar.style.opacity = '0';
    document.body.appendChild(bar);
  });
}

async function showSubtitle(page, text) {
  await page.evaluate(t => {
    const bar = document.getElementById('demo-subtitle');
    if (!bar) return;
    bar.textContent = t;
    bar.style.opacity = t ? '1' : '0';
  }, text || '');
  if (text) await page.waitForTimeout(500);
}

// ── Main recording ───────────────────────────────────────────────

(async () => {
  if (!fs.existsSync(VIDEO_DIR)) fs.mkdirSync(VIDEO_DIR, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    recordVideo: { dir: VIDEO_DIR, size: { width: W, height: H } },
    viewport: { width: W, height: H }
  });
  const page = await context.newPage();

  try {
    const simPath = 'file:///' + path.join(__dirname, 'terminal-sim.html').replace(/\\/g, '/');
    await page.goto(simPath, { waitUntil: 'domcontentloaded' });
    await injectCursor(page);
    await injectSubtitleBar(page);

    // ── Scene 1: Title (0-3s) ──
    await showSubtitle(page, 'Claude Code\n一键批量生成英文文章');
    // Move cursor over terminal area
    await page.mouse.move(200, 300, { steps: 15 });
    await page.waitForTimeout(1500);
    await page.mouse.move(540, 280, { steps: 10 });
    await page.waitForTimeout(1500);

    // ── Scene 2: Type command (3-9s) ──
    await showSubtitle(page, '一行命令，启动批量生成');
    const cmd = 'py shared/create_articles.py --sites sub-auto --per-site 3';
    await page.evaluate(t => window.animateOutput.typeCommand(t), cmd);
    // Wait for typing to complete (cmd length * 25ms ≈ 1.5s)
    await page.waitForTimeout(2200);
    await page.waitForTimeout(800);

    // ── Scene 3: Output appears (9-18s) ──
    await showSubtitle(page, 'AI 自动写作 + 配图 + 验证');
    await page.evaluate(() => window.animateOutput.show());
    // Scroll through output progressively
    await page.waitForTimeout(2000);
    await page.evaluate(() => window.animateOutput.scrollTo(300));
    await page.waitForTimeout(2000);
    await page.evaluate(() => window.animateOutput.scrollTo(700));
    await page.waitForTimeout(1500);
    await page.evaluate(() => window.animateOutput.scrollTo(1100));
    await page.waitForTimeout(1500);

    // ── Scene 4: Results + audit (18-26s) ──
    await showSubtitle(page, '审计通过，3篇文章 0 ERROR');
    await page.evaluate(() => window.animateOutput.scrollTo(1700));
    await page.waitForTimeout(2000);
    await page.evaluate(() => window.animateOutput.scrollTo(2200));
    await page.waitForTimeout(1500);
    await page.evaluate(() => window.animateOutput.scrollTo(2700));
    await page.waitForTimeout(1500);

    // ── Scene 5: Deploy + end (26-30s) ──
    await showSubtitle(page, '部署上线  https://auto.jycsd.com');
    await page.evaluate(() => window.animateOutput.scrollTo(3200));
    await page.waitForTimeout(2500);

    // End card
    await showSubtitle(page, 'Claude Code 让 AI 替你干活');
    await page.waitForTimeout(2000);
    await showSubtitle(page, '');

  } catch (err) {
    console.error('RECORDING ERROR:', err.message);
  } finally {
    await context.close();
    const video = page.video();
    if (video) {
      const src = await video.path();
      const dest = path.join(VIDEO_DIR, OUTPUT_NAME);
      try {
        fs.copyFileSync(src, dest);
        console.log('Video saved:', dest);
        console.log('Size:', (fs.statSync(dest).size / 1024 / 1024).toFixed(1), 'MB');
      } catch (e) {
        console.error('Failed to copy video:', e.message);
      }
    }
    await browser.close();
  }
})();
