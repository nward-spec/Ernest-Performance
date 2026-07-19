// Render each .frame element of a carousel HTML to a 1080x1350 PNG.
// Usage: node tools/render_frames.js <html-file> <out-dir>
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

(async () => {
  const htmlFile = process.argv[2];
  const outDir = process.argv[3] || path.dirname(htmlFile);
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch({ executablePath: CHROME });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 2 });
  await page.goto('file://' + path.resolve(htmlFile), { waitUntil: 'networkidle' });

  const frames = await page.$$('.frame');
  const base = path.basename(htmlFile).replace(/\.html?$/, '');
  const files = [];
  for (let i = 0; i < frames.length; i++) {
    const f = path.join(outDir, `${base}-frame-${i + 1}.png`);
    await frames[i].screenshot({ path: f });
    files.push(f);
    console.log('  ✓', path.basename(f));
  }
  await browser.close();
  console.log(`rendered ${files.length} frames -> ${outDir}`);
})().catch(e => { console.error(e); process.exit(1); });
