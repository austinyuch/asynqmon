import { chromium } from "playwright";
import { mkdirSync } from "node:fs";

const BASE = "http://localhost:28090";
const SHOTS = "../../.agents/specs/003-ui-mui4-to-mui5-migration/reports/smoke";
mkdirSync(SHOTS, { recursive: true });

const results = [];
const pageErrors = [];
const consoleErrors = [];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
page.on("pageerror", (e) => pageErrors.push(String(e)));
page.on("console", (m) => {
  if (m.type() === "error") consoleErrors.push(m.text().slice(0, 200));
});

async function visit(name, path, expectText, opts = {}) {
  // direct goto = deep-link refresh semantics (router 6 + SPA fallback)
  await page.goto(BASE + path, { waitUntil: "networkidle" });
  await page.waitForTimeout(400);
  let ok = true, note = "";
  if (expectText) {
    ok = await page
      .getByText(expectText, { exact: false })
      .first()
      .isVisible()
      .catch(() => false);
    note = ok ? `text "${expectText}" visible` : `text "${expectText}" NOT FOUND`;
  }
  const rootHasContent = await page.$eval("#root", (el) => el.children.length > 0).catch(() => false);
  if (!rootHasContent) { ok = false; note += " | #root empty"; }
  await page.screenshot({ path: `${SHOTS}/${name}.png`, fullPage: false });
  results.push({ name, path, ok, note });
}

await visit("01-dashboard", "/", "Queues");
await visit("02-queue-default-pending", "/queues/default?status=pending", "email:welcome");
await visit("03-queue-critical-scheduled", "/queues/critical?status=scheduled", "report:generate");
await visit("04-queue-low-archived", "/queues/low?status=archived", "image:resize");
await visit("05-servers", "/servers", "Servers");
await visit("06-schedulers", "/schedulers", "Scheduler");
await visit("07-redis", "/redis", "Redis");
await visit("08-settings", "/settings", "Settings");

// dark mode: Settings > theme select -> Always
await page.goto(BASE + "/settings", { waitUntil: "networkidle" });
await page.locator("#theme-selected").click();
await page.getByRole("option", { name: "Always" }).click();
await page.waitForTimeout(500);
// theme bg lives on the app content container (body is theme-agnostic, same as v4)
const bg = await page.evaluate(() => {
  const appBar = document.querySelector("header.MuiAppBar-root");
  return appBar ? getComputedStyle(appBar).backgroundColor : "none";
});
const darkOk = bg !== "none" && bg !== "rgb(255, 255, 255)" && bg !== "rgb(67, 121, 255)";
await page.screenshot({ path: `${SHOTS}/09-dark-mode.png` });
results.push({ name: "09-dark-mode", path: "/settings", ok: darkOk, note: `body bg=${bg}` });

// client-side navigation (router 6 Link): dashboard -> queue via row click
await page.goto(BASE + "/", { waitUntil: "networkidle" });
await page.locator('a[href*="/queues/critical"]').first().click();
await page.waitForTimeout(600);
const navUrl = page.url();
results.push({ name: "10-client-nav", path: "click queue 'critical'", ok: navUrl.includes("/queues/critical"), note: `landed: ${navUrl}` });
await page.screenshot({ path: `${SHOTS}/10-client-nav.png` });

// metrics view renders (no prometheus configured -> expect graceful UI, not crash)
await visit("11-metrics", "/queues/default", null); // re-baseline
await page.goto(BASE + "/metrics", { waitUntil: "networkidle" }).catch(() => {});
await page.waitForTimeout(400);
const metricsRoot = await page.$eval("#root", (el) => el.children.length > 0).catch(() => false);
await page.screenshot({ path: `${SHOTS}/12-metrics-no-prom.png` });
results.push({ name: "12-metrics-no-prom", path: "/metrics", ok: metricsRoot, note: "renders without crash (prometheus absent)" });

await browser.close();

console.log("=== SMOKE RESULTS ===");
let fails = 0;
for (const r of results) {
  if (!r.ok) fails++;
  console.log(`${r.ok ? "PASS" : "FAIL"}  ${r.name}  ${r.path}  ${r.note}`);
}
console.log(`pageErrors: ${pageErrors.length}`);
pageErrors.slice(0, 5).forEach((e) => console.log("  PAGEERR: " + e.slice(0, 200)));
console.log(`consoleErrors: ${consoleErrors.length}`);
consoleErrors.slice(0, 8).forEach((e) => console.log("  CONSOLE: " + e));
process.exit(fails > 0 || pageErrors.length > 0 ? 1 : 0);
