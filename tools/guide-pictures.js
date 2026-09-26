#!/usr/bin/env node
/* Retake the staff guide's screenshots and print its PDF.

   Run from anywhere after the app looks different:
       node tools/guide-pictures.js

   It takes the pictures in manual/img/ on a 412 x 915 phone screen
   (Settings at its full 600 px width), measures where the numbered callouts go (manual/boxes.json), rebuilds
   manual/index.html with tools/manual.py, then prints
   manual/Talanoa-Staff-Guide.pdf.

   Needs Chromium and Node's playwright-core. If they aren't found, say where:
       CHROMIUM=/usr/bin/chromium  PLAYWRIGHT_CORE=/path/to/node_modules/playwright-core
   and PYTHON=/path/to/python (with qrcode installed) for tools/manual.py. */
'use strict';
const fs = require('fs'), path = require('path'), http = require('http'), { execFileSync } = require('child_process');
const { chromium } = require(process.env.PLAYWRIGHT_CORE || 'playwright-core');

const ROOT = path.resolve(__dirname, '..');
const IMG = path.join(ROOT, 'manual', 'img');
const PHONE = { width: 412, height: 915 };
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.css': 'text/css',
  '.webmanifest': 'application/manifest+json', '.png': 'image/png', '.webp': 'image/webp', '.jpg': 'image/jpeg',
  '.mp3': 'audio/mpeg', '.svg': 'image/svg+xml', '.pdf': 'application/pdf' };

/* A tiny web server for the repo, so the app runs just as it does online (offline cache and all). */
function serve() {
  const server = http.createServer((req, res) => {
    let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    if (p.endsWith('/')) p += 'index.html';
    const file = path.join(ROOT, path.normalize(p));
    if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise((ok) => server.listen(0, '127.0.0.1', () => ok(server)));
}

(async () => {
  const server = await serve();
  const URL0 = `http://127.0.0.1:${server.address().port}/`;
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/usr/bin/chromium', headless: true });
  const ctx = await browser.newContext({ viewport: PHONE, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const page = await ctx.newPage();
  const converter = await ctx.newPage();

  async function webp(png, name) {                     // Chromium turns the PNG into a WebP for us
    const url = await converter.evaluate(async (b64) => {
      const im = new Image(); im.src = 'data:image/png;base64,' + b64; await im.decode();
      const c = document.createElement('canvas'); c.width = im.width; c.height = im.height;
      c.getContext('2d').drawImage(im, 0, 0);
      return c.toDataURL('image/webp', 0.82);
    }, png.toString('base64'));
    fs.writeFileSync(path.join(IMG, name), Buffer.from(url.split(',')[1], 'base64'));
    console.log('  manual/img/' + name);
  }
  const cdp = await ctx.newCDPSession(page);
  async function tap(sel, i) {                        // a real finger tap, as on the phone
    const b = await page.evaluate(([s, i]) => { const r = document.querySelectorAll(s)[i].getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; }, [sel, i]);
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: b[0], y: b[1] }] });
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    await page.waitForTimeout(700);                   // let the green flash finish
  }
  const goTo = (name) => page.evaluate((n) => { current = pages.findIndex((p) => p.name === n); render(''); }, name);
  const tileIndex = (label) => page.evaluate((l) => [...document.querySelectorAll('#stage .tile')].findIndex((t) => t.textContent.trim() === l), label);
  const box = (sel) => page.evaluate((s) => { const r = document.querySelector(s).getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height }; }, sel);
  const still = () => page.addStyleTag({ content: '*,*::after{animation:none!important;transition:none!important}' });

  // Open once so it installs for offline use, save the voice, then open again (Settings then shows "Ready")
  await page.goto(URL0);
  await page.waitForFunction(() => navigator.serviceWorker.controller, null, { timeout: 30000 });
  await page.waitForFunction(async () => {
    const want = voiceUrls(), have = new Set((await (await caches.open('tt-voices')).keys()).map((r) => r.url));
    return want.every((u) => have.has(u));
  }, null, { timeout: 120000, polling: 500 });
  await page.reload();
  await page.waitForSelector('#stage .tile');
  await still();
  // "N tiles play your own recording" only shows when the app runs from this computer, never online
  await page.evaluate(() => { document.getElementById('clipStat').hidden = true; showMineStat = () => {}; });

  console.log('Screenshots:');
  const boxes = { shot: PHONE };
  // 1. main screen, just after tapping Hug on "I want"
  await goTo('I want');
  await tap('#stage .tile', await tileIndex('Hug'));
  for (const [k, s] of Object.entries({ banner: '#banner', core: '#core', prev: '#prev', title: '#title', next: '#next', stage: '#stage', gear: '#gear' })) boxes[k] = await box(s);
  boxes.snack = await box('#stage .tile:nth-child(1)');
  boxes.lit = await box('#stage .tile.lit');
  await webp(await page.screenshot(), 'main.webp');
  // 2. talking: the Maverik page after Drink
  await goTo('Maverik');
  await tap('#stage .tile', await tileIndex('Drink'));
  await webp(await page.screenshot(), 'portrait.webp');
  await page.evaluate(() => { litItem = null; lightUp(); said.textContent = HINT; });
  // 3. the page list
  await page.evaluate(() => openPicker());
  await webp(await page.screenshot(), 'picker.webp');
  await page.evaluate(() => picker.classList.remove('open'));
  // 4. pages
  for (const [name, file] of [['Ouch', 'page-ouch.webp'], ['Questions', 'page-questions.webp'], ['Mom & Dad', 'momdad.webp']]) {
    await goTo(name); await webp(await page.screenshot(), file);
  }
  // 5. Settings at its full width (600 px, as on a tablet: it prints better), tall enough to
  //    show the whole sheet, cut into two pictures
  await page.setViewportSize({ width: 632, height: 2600 });
  await page.evaluate(() => openSettings());
  await page.waitForFunction(() => /Ready to use/.test(document.getElementById('offlineStat').textContent) && /Version \w/.test(document.getElementById('updateStat').textContent), null, { timeout: 15000 });
  const sheet = await box('#panel .sheet');
  const S = await page.evaluate(() => {
    const s = document.querySelector('#panel .sheet').getBoundingClientRect();
    const R = (a, b) => { const r = a.getBoundingClientRect(), q = (b || a).getBoundingClientRect();
      return { x: r.x - s.x, y: r.y - s.y, width: r.width, height: q.bottom - r.top, sheetW: s.width, sheetH: s.height }; };
    const pagesH3 = [...document.querySelectorAll('#panel h3')].find((h) => h.textContent === 'Pages to show');
    return {
      s_voice: R(document.getElementById('voiceList')), s_speed: R(document.getElementById('speed')), s_vol: R(document.getElementById('vol')),
      s_pages: R(pagesH3, document.getElementById('pageList')), s_swipe: R(document.getElementById('swipeOn').closest('label')),
      s_status: R(document.getElementById('offlineStat')), s_update: R(document.getElementById('checkUpdate')),
      s_about: R(document.querySelector('#panel a[href="credits.html"]')), s_done: R(document.getElementById('closePanel')),
    };
  });
  Object.assign(boxes, S);
  const cut = S.s_pages.y - 44;                        // tools/manual.py cuts in the same place
  await webp(await page.screenshot({ clip: { x: sheet.x, y: sheet.y, width: sheet.width, height: cut } }), 'settings-top.webp');
  await webp(await page.screenshot({ clip: { x: sheet.x, y: sheet.y + cut, width: sheet.width, height: sheet.height - cut } }), 'settings-bottom.webp');

  fs.writeFileSync(path.join(ROOT, 'manual', 'boxes.json'), JSON.stringify(boxes, null, 1) + '\n');
  console.log('  manual/boxes.json');

  // Rebuild the guide with the new pictures, then print it
  execFileSync(process.env.PYTHON || 'python3', [path.join(ROOT, 'tools', 'manual.py')], { stdio: 'inherit' });
  const doc = await ctx.newPage();
  await doc.goto(URL0 + 'manual/', { waitUntil: 'networkidle' });
  await doc.emulateMedia({ media: 'print' });
  await doc.pdf({ path: path.join(ROOT, 'manual', 'Talanoa-Staff-Guide.pdf'), preferCSSPageSize: true, printBackground: true });
  console.log('  manual/Talanoa-Staff-Guide.pdf');

  await browser.close();
  server.close();
})().catch((e) => { console.error(e); process.exit(1); });
