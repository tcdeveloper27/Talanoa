#!/usr/bin/env node
/* Retake the staff guide's screenshots and print its PDF.

   Run from anywhere after the app looks different:
       node tools/guide-pictures.js

   It takes the pictures in manual/img/ on a 412 x 915 phone screen
   (Settings at its full 600 px width), measures where the numbered callouts go (manual/boxes.json), rebuilds
   manual/index.html with tools/manual.py, then prints
   manual/Talanoa-Staff-Guide.pdf, the paper board, manual/Talanoa-Paper-Board.pdf, and the health pages,
   manual/Talanoa-Health-Pages.pdf.

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

  /* Chromium turns the PNG into a WebP for us. This runs in the app's own page (a second page
     would put the app in the background and freeze its sparkle loop mid-screenshot). */
  async function webp(png, name) {
    const url = await page.evaluate(async (b64) => {
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
  /* wait for the last tap's sparkles to finish before moving on, so a page picture doesn't show another page's fun */
  const calm = () => page.waitForFunction(() => !window.FX || FX.count() === 0, null, { timeout: 8000 });
  const goTo = async (name) => { await calm(); await page.evaluate((n) => { current = pages.findIndex((p) => p.name === n); render(''); }, name); };
  const tileIndex = (label) => page.evaluate((l) => [...document.querySelectorAll('#stage .tile')].findIndex((t) => t.textContent.trim() === l), label);
  const box = (sel) => page.evaluate((s) => { const r = document.querySelector(s).getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height }; }, sel);
  const still = () => page.addStyleTag({ content: '*,*::after,*::before{animation:none!important;transition:none!important}' });

  // Open once so it installs for offline use, save the voice, then open again (Settings then shows "Ready").
  // (waitForFunction doesn't wait for an async check, so this polls by hand.)
  await page.goto(URL0);
  await page.waitForFunction(() => navigator.serviceWorker.controller, null, { timeout: 30000 });
  // (2026-10-08: twice the count stopped short of the end; why wasn't caught, so if it stops rising for 20 s the app is
  // asked to carry on saving, which fetches whatever is still missing)
  for (let end = Date.now() + 300000, last = -1, since = Date.now(); ;) {   // ~9,300 clips through this small server
    const left = await page.evaluate(async () => {
      const want = voiceUrls(), have = new Set((await (await caches.open('tt-voices')).keys()).map((r) => r.url));
      return want.filter((u) => !have.has(u)).length;
    });
    if (left === 0) break;
    if (left !== last) { last = left; since = Date.now(); }
    else if (Date.now() - since > 20000) { await page.evaluate(() => warmVoice()); since = Date.now(); }
    if (Date.now() > end) throw new Error('the voice did not finish saving for offline use (' + left + ' clips left)');
    await page.waitForTimeout(500);
  }
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
  await calm();
  // 3. the page list
  await page.evaluate(() => openPicker());
  await webp(await page.screenshot(), 'picker.webp');
  await page.evaluate(() => picker.classList.remove('open'));
  // 4. pages
  for (const [name, file] of [['Ouch', 'page-ouch.webp'], ['Questions', 'page-questions.webp'], ['Mom & Dad', 'momdad.webp'], ['Body', 'page-body.webp']]) {
    await goTo(name); await webp(await page.screenshot(), file);
  }
  // 5. the Talk and Tongan pages, each just after a tap
  for (const [name, label, file] of [['Talk', 'I like it', 'page-talk.webp'], ['Tongan', 'Mālō', 'page-tongan.webp']]) {
    await goTo(name);
    await tap('#stage .tile', await page.evaluate((l) => [...document.querySelectorAll('#stage .tile')].findIndex((t) => t._item.label === l), label));
    await calm();
    await webp(await page.screenshot(), file);
  }
  // 6. the ABC page with a word typed and spoken
  await goTo('ABC');
  await page.evaluate(() => { typed = 'HI MOM'; showTyped(); show('HI MOM', null); });
  await webp(await page.screenshot(), 'abc.webp');
  await page.evaluate(() => { typed = ''; showTyped(); });
  // 7. the about-me message ("Hi, I'm Brenton" on the top row), shown big by tapping the words at the top
  await goTo('People');
  await page.evaluate(() => { speechSynthesis.speak = () => {}; });
  await tap('#core .core-btn', await page.evaluate(() => [...document.querySelectorAll('#core .core-btn')].findIndex((b) => b._item.card)));
  await page.evaluate(() => openShow(said.textContent));
  await webp(await page.screenshot(), 'show-big.webp');
  await page.evaluate(() => { closeShow(); litItem = null; lightUp(); said.textContent = HINT; });
  await calm();
  // 8. Settings at its full width (600 px, as on a tablet: it prints better), tall enough to
  //    show the whole sheet, cut into three pictures. A week of example counts, so "Most-used
  //    pictures" has something to show.
  await page.evaluate(() => {
    const d = (n) => dayStr(new Date(Date.now() - n * 864e5));
    localStorage.setItem('tt_counts', JSON.stringify({ since: d(6), days: {
      [d(0)]: { 'I want|Drink': 4, 'I feel|Happy': 3, 'core|Yes': 3, 'Maverik|Drink': 2 },
      [d(2)]: { 'I want|Drink': 3, 'I feel|Happy': 2, 'Fun|Toy Story': 3 },
      [d(5)]: { 'Maverik|Drink': 3, 'core|Yes': 2, "core|Hi, I'm Brenton": 3 } } }));
  });
  await page.setViewportSize({ width: 632, height: 3600 });
  await page.evaluate(() => openSettings());
  await page.waitForFunction(() => /Ready to use/.test(document.getElementById('offlineStat').textContent) && /Version \w/.test(document.getElementById('updateStat').textContent), null, { timeout: 15000 });
  // the sheet is at most 92% of the screen's height: make the screen tall enough to show all of it, Done included
  const tall = await page.evaluate(() => document.querySelector('#panel .sheet').scrollHeight);
  await page.setViewportSize({ width: 632, height: Math.ceil(tall / 0.92) + 40 });
  await page.waitForTimeout(300);
  const sheet = await box('#panel .sheet');
  const S = await page.evaluate(() => {
    const s = document.querySelector('#panel .sheet').getBoundingClientRect();
    const R = (a, b) => { const r = a.getBoundingClientRect(), q = (b || a).getBoundingClientRect();
      return { x: r.x - s.x, y: r.y - s.y, width: r.width, height: q.bottom - r.top, sheetW: s.width, sheetH: s.height }; };
    const h3 = (t) => [...document.querySelectorAll('#panel h3')].find((h) => h.textContent === t);
    const lab = (id) => document.getElementById(id).closest('label');
    return {
      s_voice: R(document.getElementById('voiceList')), s_speed: R(document.getElementById('speed')), s_vol: R(document.getElementById('vol')),
      s_pages: R(h3('Pages to show'), document.getElementById('pageList')), s_find: R(h3('Find a word'), document.getElementById('findBox')), s_swipe: R(lab('swipeOn')),
      s_fx: R(document.getElementById('fxList')), s_calm: R(lab('calmOn')), s_big: R(lab('bigOn')), s_strong: R(lab('strongOn')),
      s_sent: R(h3('Talking in sentences'), lab('recentOn')), s_screen: R(h3('Screen'), lab('roomOn')),
      s_own: R(h3('Photos and voices')), s_ownbtn: R(document.getElementById('ownOpen')), s_backup: R(document.getElementById('ownSave').parentNode),
      s_counts: R(document.getElementById('countSpan'), document.getElementById('unusedBox')), s_counton: R(lab('countOn'), document.getElementById('countClear')),
      s_status: R(document.getElementById('offlineStat')), s_update: R(document.getElementById('checkUpdate')),
      s_links: R(document.querySelector('#panel a[href="manual/"]'), document.querySelector('#panel a[href="credits.html"]')),
      s_done: R(document.getElementById('closePanel')),
    };
  });
  Object.assign(boxes, S);
  // cut halfway between two sections, so no slider or option is cut in two (tools/manual.py cuts in the same places)
  const mid = (a, b) => Math.round((a.y + a.height + b.y) / 2);
  const cuts = [0, mid(S.s_vol, S.s_pages), mid(S.s_screen, S.s_own), sheet.height];
  for (const [i, name] of [[0, 'settings-top.webp'], [1, 'settings-mid.webp'], [2, 'settings-bottom.webp']])
    await webp(await page.screenshot({ clip: { x: sheet.x, y: sheet.y + cuts[i], width: sheet.width, height: cuts[i + 1] - cuts[i] } }), name);

  // 9. changing one picture's photo and voice: the Mālō tile on the Tongan page
  await page.evaluate(() => {
    panel.classList.remove('open');
    chooserAt = chooserLists().findIndex((p) => p.name === 'Tongan'); openChooser();
    [...document.querySelectorAll('#chooserGrid .tile')].find((t) => t._item.label === 'Mālō').click();
  });
  await page.waitForTimeout(300);
  const ed = await box('#editor .sheet');
  await webp(await page.screenshot({ clip: { x: ed.x, y: ed.y, width: ed.width, height: ed.height } }), 'editor.webp');
  await page.evaluate(() => { closeEditor(); closeChooser(); });

  fs.writeFileSync(path.join(ROOT, 'manual', 'boxes.json'), JSON.stringify(boxes, null, 1) + '\n');
  console.log('  manual/boxes.json');

  // Rebuild the guide with the new pictures, then print it
  execFileSync(process.env.PYTHON || 'python3', [path.join(ROOT, 'tools', 'manual.py')], { stdio: 'inherit' });
  // the guide is kept on the phone for offline use, so the offline list (and its version) must follow it
  execFileSync(process.env.PYTHON || 'python3', [path.join(ROOT, 'tools', 'build.py'), '--offline-list'], { stdio: 'inherit' });
  const doc = await ctx.newPage();
  await doc.goto(URL0 + 'manual/', { waitUntil: 'networkidle' });
  await doc.emulateMedia({ media: 'print' });
  await doc.pdf({ path: path.join(ROOT, 'manual', 'Talanoa-Staff-Guide.pdf'), preferCSSPageSize: true, printBackground: true });
  console.log('  manual/Talanoa-Staff-Guide.pdf');

  // The paper board: a picture of one sheet for the guide, and the ready-to-print PDF
  const paper = await ctx.newPage();
  await paper.setViewportSize({ width: 820, height: 1100 });
  await paper.goto(URL0 + 'print.html', { waitUntil: 'networkidle' });
  await paper.waitForFunction(() => window.TT_PRINT_READY && [...document.images].every((i) => i.complete), null, { timeout: 20000 });
  await paper.addStyleTag({ content: '.bar{display:none !important}' });   // the on-screen toolbar would cover the sheet's name
  const talkSheet = await paper.evaluate(() => {
    const s = [...document.querySelectorAll('.sheet')].find((x) => /Talk/.test((x.querySelector('.head b') || {}).textContent || ''));
    s.scrollIntoView(); const r = s.getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height };
  });
  const shot = await paper.screenshot({ clip: talkSheet });
  await webp(shot, 'paper.webp');
  await paper.emulateMedia({ media: 'print' });
  await paper.pdf({ path: path.join(ROOT, 'manual', 'Talanoa-Paper-Board.pdf'), preferCSSPageSize: true, printBackground: true });
  console.log('  manual/Talanoa-Paper-Board.pdf');
  // ... and just the health pages, for doctor visits (Settings → Health pages to print)
  await paper.goto(URL0 + 'print.html?pages=Ouch,Body,Sick', { waitUntil: 'networkidle' });
  await paper.waitForFunction(() => window.TT_PRINT_READY && [...document.images].every((i) => i.complete), null, { timeout: 20000 });
  await paper.pdf({ path: path.join(ROOT, 'manual', 'Talanoa-Health-Pages.pdf'), preferCSSPageSize: true, printBackground: true });
  console.log('  manual/Talanoa-Health-Pages.pdf');

  await browser.close();
  server.close();
})().catch((e) => { console.error(e); process.exit(1); });
