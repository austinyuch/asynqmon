import { test, expect, type Page } from "@playwright/test";

// Functional E2E smoke — the CI gate (SPEC-005 / REQ-QG-001).
// Asserts against the canonical demo scenario (docs/manual/demo/main.go):
// every task state seeded, `low` queue paused with pending tasks, one live
// worker, two scheduler entries. No VRT here by design — pixel baselines
// stay local-only (manual-screenshots.spec.ts) to avoid cross-runner font
// false-reds.
const consoleErrors: string[] = [];

test.beforeEach(({ page }) => {
  page.on("pageerror", (e) => consoleErrors.push(`pageerror: ${e}`));
  page.on("console", (m) => {
    if (m.type() === "error") consoleErrors.push(m.text().slice(0, 160));
  });
});

async function go(page: Page, path: string) {
  await page.goto(path, { waitUntil: "networkidle" });
  await page.waitForTimeout(300);
}

test("dashboard lists queues with paused state", async ({ page }) => {
  await go(page, "/");
  for (const q of ["critical", "default", "low"]) {
    await expect(page.getByText(q, { exact: true }).first()).toBeVisible();
  }
  await expect(page.getByText("paused").first()).toBeVisible();
});

test("every task state tab shows seeded data (deep-link refresh)", async ({ page }) => {
  const cases: Array<[string, string]> = [
    ["/queues/default?status=active", "video:transcode"],
    ["/queues/low?status=pending", "image:resize"],
    ["/queues/critical?status=scheduled", "report:generate"],
    ["/queues/default?status=retry", "sync:export"],
    ["/queues/critical?status=archived", "billing:charge"],
    ["/queues/default?status=completed", "email:"],
  ];
  for (const [path, expected] of cases) {
    await go(page, path);
    await expect(page.getByText(expected).first()).toBeVisible();
  }
});

test("aggregating tab lists tasks after picking a group", async ({ page }) => {
  await go(page, "/queues/default?status=aggregating");
  // the tab requires choosing a group before tasks render
  await page.getByRole("combobox").first().click();
  await page.getByRole("option", { name: "metrics-batch" }).click();
  await page.waitForTimeout(400);
  await expect(page.getByText("metrics:event").first()).toBeVisible();
});

test("task details opens from a row click (client-side nav)", async ({ page }) => {
  await go(page, "/queues/default?status=retry");
  await page.getByText("sync:export").first().click();
  await page.waitForTimeout(500);
  expect(page.url()).toContain("/tasks/");
  await expect(page.getByText("sync:export").first()).toBeVisible();
});

test("servers page shows the live worker", async ({ page }) => {
  await go(page, "/servers");
  await expect(page.getByText(/active/i).first()).toBeVisible();
  await expect(page.getByText("critical").first()).toBeVisible(); // queue priorities listed
});

test("schedulers page lists cron entries", async ({ page }) => {
  await go(page, "/schedulers");
  await expect(page.getByText("report:generate").first()).toBeVisible();
  await expect(page.getByText("cleanup:tmp").first()).toBeVisible();
});

test("dark mode toggles the MUI palette", async ({ page }) => {
  await go(page, "/settings");
  await page.locator("#theme-selected").click();
  await page.getByRole("option", { name: "Always" }).click();
  await page.waitForTimeout(500);
  const bg = await page.evaluate(
    () => getComputedStyle(document.querySelector("header.MuiAppBar-root")!).backgroundColor
  );
  expect(bg).toBe("rgb(18, 18, 18)");
  // restore
  await page.locator("#theme-selected").click();
  await page.getByRole("option", { name: "Never" }).click();
});

test.afterAll(() => {
  expect(consoleErrors, `console errors: ${consoleErrors.join(" | ")}`).toHaveLength(0);
});
