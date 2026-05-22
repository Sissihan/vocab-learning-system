/**
 * Capture UI screenshots for operation manuals (en + zh-CN).
 * Run: node docs/capture-screenshots.mjs
 */
import { chromium } from "playwright";
import { mkdir, writeFile } from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, "screenshots");
const BASE = "http://127.0.0.1:3000";
const API = "http://127.0.0.1:8000";

async function getToken() {
  const res = await fetch(`${API}/api/auth/login/json`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: "demo", password: "demo123" }),
  });
  const data = await res.json();
  return data.access_token;
}

async function shot(page, name, fullPage = true) {
  const file = path.join(OUT, `${name}.png`);
  await page.screenshot({ path: file, fullPage });
  console.log("  saved", name);
  return file;
}

async function setLocale(page, locale) {
  await page.addInitScript((loc) => {
    localStorage.setItem("vocab_locale", loc);
  }, locale);
}

async function setAuth(page, token) {
  await page.addInitScript((t) => {
    localStorage.setItem("token", t);
  }, token);
}

async function captureLocale(browser, locale, prefix) {
  const token = await getToken();
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    locale: locale === "en" ? "en-US" : "zh-CN",
  });
  const page = await context.newPage();
  await setLocale(page, locale);
  await setAuth(page, token);

  // Login (show language + form)
  await page.goto(`${BASE}/login`);
  await page.waitForTimeout(1500);
  await shot(page, `${prefix}-01-login`);

  // Dashboard - fragment
  await page.goto(`${BASE}/dashboard`);
  await page.waitForSelector("h1", { timeout: 15000 });
  await page.waitForTimeout(2000);
  await shot(page, `${prefix}-02-dashboard-fragment`);

  // Dashboard - focus scene
  const focusTab = locale === "en" ? "Focus" : "专注";
  const commuteTab = locale === "en" ? "Commute" : "通勤";
  try {
    await page.getByRole("button", { name: new RegExp(focusTab, "i") }).click();
    await page.waitForTimeout(2500);
    await shot(page, `${prefix}-03-dashboard-focus`);
  } catch (e) {
    console.warn("  focus tab skip", e.message);
  }

  // Learn - first recommended word
  const learnLink = page.locator('a[href*="word_id"]').first();
  if (await learnLink.count()) {
    const href = await learnLink.getAttribute("href");
    await page.goto(`${BASE}${href}`);
    await page.waitForTimeout(1500);
    await shot(page, `${prefix}-04-learn-hidden`);
    const showBtn = locale === "en" ? /Show definition/i : /显示释义/;
    await page.getByRole("button", { name: showBtn }).click();
    await page.waitForTimeout(1500);
    await shot(page, `${prefix}-05-learn-revealed`);
  } else {
    await page.goto(`${BASE}/learn?word_id=1&scene=focus`);
    await page.waitForTimeout(2000);
    await shot(page, `${prefix}-04-learn`);
  }

  // Games
  await page.goto(`${BASE}/games`);
  await page.waitForTimeout(2000);
  await shot(page, `${prefix}-06-games-puzzle`);

  const matchLabel = locale === "en" ? "Semantic match" : "语义连线";
  await page.getByRole("button", { name: new RegExp(matchLabel, "i") }).click();
  await page.waitForTimeout(2000);
  await shot(page, `${prefix}-07-games-match`);

  const planetLabel = locale === "en" ? "Word planet" : "词汇星球";
  await page.getByRole("button", { name: new RegExp(planetLabel, "i") }).click();
  await page.waitForTimeout(2000);
  await shot(page, `${prefix}-08-games-planet`);

  // Profile
  await page.goto(`${BASE}/profile`);
  await page.waitForTimeout(2000);
  await shot(page, `${prefix}-09-profile`);

  // Register page
  await page.evaluate(() => localStorage.removeItem("token"));
  await page.goto(`${BASE}/register`);
  await page.waitForTimeout(1500);
  await shot(page, `${prefix}-10-register`);

  await context.close();
}

async function main() {
  await mkdir(OUT, { recursive: true });
  const browser = await chromium.launch({ headless: true });

  console.log("Capturing English (en)...");
  await captureLocale(browser, "en", "en");

  console.log("Capturing Simplified Chinese (zh-CN)...");
  await captureLocale(browser, "zh-CN", "zh");

  await browser.close();
  console.log("Done. Screenshots in docs/screenshots/");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
