// Duman testi: index.html'i Chromium'da açar, dört görünümü, aramayı, testi ve mobil genişliği dener.
// Kullanım:  node tests/smoke.mjs [ekran-görüntüsü-klasörü]
// CDN erişimi olmayan ortamlarda ATLAS_LIB_DIR=<node_modules yolu> verilirse Leaflet ve vis-network
// istekleri bu klasördeki aynı sürümlerden karşılanır (npm i leaflet@1.9.4 vis-network@9.1.9).
import { createRequire } from "module";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const here = path.dirname(fileURLToPath(import.meta.url));
const url = "file://" + path.resolve(here, "..", "index.html");
const shots = process.argv[2];
const libDir = process.env.ATLAS_LIB_DIR;
if (shots) fs.mkdirSync(shots, { recursive: true });

const LIBS = {
  "leaflet/1.9.4/leaflet.js": ["leaflet/dist/leaflet.js", "application/javascript"],
  "leaflet/1.9.4/leaflet.css": ["leaflet/dist/leaflet.css", "text/css"],
  "vis-network@9.1.9/standalone/umd/vis-network.min.js": ["vis-network/standalone/umd/vis-network.min.js", "application/javascript"],
};

let failures = 0;
const ok = (cond, msg) => { console.log(`${cond ? "✓" : "✗"} ${msg}`); if (!cond) failures++; };

async function newPage(browser, opts) {
  const ctx = await browser.newContext(opts);
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push("pageerror: " + e.message));
  page.on("console", (m) => { if (m.type() === "error") errors.push("console: " + m.text()); });
  await page.route("**/*", (route) => {
    const u = route.request().url();
    if (u.startsWith("file://")) return route.continue();
    const hit = Object.keys(LIBS).find((k) => u.endsWith(k));
    if (hit && libDir) return route.fulfill({ path: path.join(libDir, LIBS[hit][0]), contentType: LIBS[hit][1] });
    if (/basemaps\.cartocdn\.com|tile\.openstreetmap/.test(u)) return route.abort();
    return route.continue();
  });
  await page.goto(url);
  await page.waitForFunction(() => document.querySelector("#counts")?.textContent.length > 0);
  return { ctx, page, errors };
}

const browser = await chromium.launch();
try {
  // ---- Masaüstü ----
  const { ctx, page, errors } = await newPage(browser, { viewport: { width: 1366, height: 900 } });
  ok(await page.evaluate(() => typeof L !== "undefined"), "Leaflet yüklendi");
  ok(await page.evaluate(() => typeof vis !== "undefined"), "vis-network yüklendi");

  const markers = await page.locator("#map path.leaflet-interactive").count();
  ok(markers > 30, `Harita: ${markers} şehir işareti`);
  if (shots) await page.screenshot({ path: path.join(shots, "1-harita.png") });

  // Yıl kaydırıcısı
  await page.uncheck("#year-all");
  await page.locator("#year").evaluate((el) => { el.value = "1070"; el.dispatchEvent(new Event("input", { bubbles: true })); });
  const aliveTxt = await page.locator("#alive").innerText();
  ok(/1070 yılında hayatta/.test(aliveTxt) && aliveTxt.includes("Kaşgarlı Mahmud"), "Yıl 1070: Kaşgarlı Mahmud hayatta görünüyor");
  ok(!aliveTxt.includes("Mimar Sinan"), "Yıl 1070: Mimar Sinan görünmüyor");
  await page.click("#play"); await page.waitForTimeout(700); await page.click("#play");
  const yr = +(await page.locator("#year-out").innerText());
  ok(yr > 1070, `Oynat düğmesi zamanı ilerletti (${yr})`);
  await page.check("#year-all");

  // Arama (aksansız)
  await page.fill("#q", "divanu lugat");
  const first = await page.locator("#q-results li").first().innerText();
  ok(/Divanü Lügati't-Türk/.test(first), `Arama "divanu lugat" → ${first.split("\n")[1] || first.split("\n")[0]}`);
  await page.fill("#q", "farabi");
  ok(/Farabi/.test(await page.locator("#q-results li").first().innerText()), 'Arama "farabi" → Farabi');
  await page.fill("#q", "muallim-i sani");
  ok(/Farabi/.test(await page.locator("#q-results li").first().innerText()), 'Arama lakapla "muallim-i sani" → Farabi');
  await page.fill("#q", "Kutadgu");
  await page.keyboard.press("Enter");
  ok(await page.locator("#detail").isVisible(), "Aramadan seçim detay panelini açtı");
  ok(/Yusuf Has Hacib/.test(await page.locator("#detail-body").innerText()), "Detay: Kutadgu Bilig yazarı görünüyor");

  // Detaydan kişiye, sonra haritada güzergâh
  await page.click('#detail-body [data-go="yusuf-has-hacib"]');
  await page.click('#detail-body [data-nav="harita"]');
  const route = await page.locator("#route-info").innerText();
  ok(/Balasagun → Kâşgar/.test(route), `Haritada güzergâh: ${route}`);
  ok(await page.locator(".route-num").count() >= 2, "Güzergâh numaraları çizildi");
  await page.waitForTimeout(600); // fitBounds animasyonu
  if (shots) await page.screenshot({ path: path.join(shots, "2-guzergah.png") });

  // Zaman çizelgesi
  await page.click("#tab-zaman");
  const bars = await page.locator("#timeline .bar").count();
  const workMarks = await page.locator("#timeline rect.work").count();
  ok(bars >= 100, `Zaman çizelgesi: ${bars} ömür çubuğu`);
  ok(workMarks >= 100, `Zaman çizelgesi: ${workMarks} eser işareti`);
  await page.locator('#timeline .bar[data-pid="biruni"] rect.life').click();
  ok(/Bîrûnî/.test(await page.locator("#detail-body").innerText()), "Çubuğa tıklama detay açtı");
  if (shots) await page.screenshot({ path: path.join(shots, "3-zaman.png") });

  // İlişki ağı
  await page.click('#detail-body [data-nav="ag"]');
  await page.waitForSelector("#network canvas");
  await page.waitForTimeout(2500);
  const netInfo = await page.evaluate(() => ({ canvas: !!document.querySelector("#network canvas") }));
  ok(netInfo.canvas, "Ağ çizildi (canvas)");
  ok(await page.locator("#legend li").count() >= 7, "Ağ göstergesi kenar türlerini listeliyor");
  if (shots) await page.screenshot({ path: path.join(shots, "4-ag.png") });

  // Filtre
  await page.selectOption("#f-dil", "Farsça");
  await page.click("#tab-sinav");
  const farsCards = await page.locator("#cards .card").count();
  ok(farsCards > 10 && farsCards < 60, `Dil filtresi (Farsça): ${farsCards} kart`);
  await page.click("#f-reset");

  // Sınav kartları
  const cards = await page.locator("#cards .card").count();
  ok(cards === 174, `Sınav kartları: ${cards}`);
  await page.locator("#cards .card").first().click();
  ok(await page.locator("#cards .card.flipped").count() === 1, "Kart çevrildi");
  if (shots) await page.screenshot({ path: path.join(shots, "5-kartlar.png") });
  await page.click('[data-sub="karistirilanlar"]');
  ok(await page.locator(".pair").count() >= 3, `Karıştırılanlar: ${await page.locator(".pair").count()} çift`);
  await page.click('[data-sub="test"]');
  for (let i = 0; i < 3; i++) {
    await page.locator("#quiz [data-opt]").first().click();
    await page.click("#quiz-next");
  }
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem("atlas.quiz.v1") || "null"));
  ok(saved && saved.dogru + saved.yanlis === 3, "Test ilerlemesi localStorage'a kaydedildi");
  if (shots) await page.screenshot({ path: path.join(shots, "6-test.png") });

  // Koyu tema
  await page.click("#theme-btn"); await page.click("#theme-btn");
  ok(await page.evaluate(() => document.documentElement.dataset.theme === "dark"), "Koyu tema etkin");
  await page.click("#tab-harita");
  if (shots) await page.screenshot({ path: path.join(shots, "7-koyu.png") });

  ok(errors.length === 0, `Masaüstünde konsol hatası yok${errors.length ? ": " + errors.join(" | ") : ""}`);
  await ctx.close();

  // ---- Mobil (390 px) ----
  const m = await newPage(browser, { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  for (const tab of ["harita", "zaman", "ag", "sinav"]) {
    await m.page.click(`#tab-${tab}`);
    await m.page.waitForTimeout(tab === "ag" ? 1500 : 300);
    const sw = await m.page.evaluate(() => document.documentElement.scrollWidth);
    ok(sw <= 390, `Mobil ${tab}: yatay kaydırma yok (scrollWidth=${sw})`);
    if (shots) await m.page.screenshot({ path: path.join(shots, `m-${tab}.png`), fullPage: false });
  }
  await m.page.click("#tab-harita");
  await m.page.fill("#q", "mevlana");
  await m.page.keyboard.press("Enter");
  const sw = await m.page.evaluate(() => document.documentElement.scrollWidth);
  ok(sw <= 390, `Mobil detay paneli açıkken yatay kaydırma yok (scrollWidth=${sw})`);
  if (shots) await m.page.screenshot({ path: path.join(shots, "m-detay.png") });
  ok(m.errors.length === 0, `Mobilde konsol hatası yok${m.errors.length ? ": " + m.errors.join(" | ") : ""}`);
  await m.ctx.close();
} finally {
  await browser.close();
}
console.log(failures ? `\n${failures} kontrol başarısız.` : "\nTüm kontroller geçti.");
process.exit(failures ? 1 : 0);
