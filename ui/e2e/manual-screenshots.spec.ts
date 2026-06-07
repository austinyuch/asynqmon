import { test, expect, type Page } from "@playwright/test";

// Manual evidence capture (docs/MANUAL_GENERATION_GUIDE.md).
// Requires the canonical demo scenario (docs/manual/demo) running against a
// registry-governed Valkey + asynqmon server: every task state is live,
// the `low` queue is paused with pending tasks, one worker and two
// scheduler entries are registered.
const ASSETS = "../docs/manual/assets";

async function settle(page: Page) {
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(500);
}

async function shot(page: Page, path: string, name: string) {
  await page.goto(path);
  await settle(page);
  await page.screenshot({ path: `${ASSETS}/${name}.png` });
}

test.describe("manual screenshots (live seeded data)", () => {
  test("dashboard + queue task states", async ({ page }) => {
    await shot(page, "/", "dashboard-overview-01-queues");
    await shot(page, "/queues/default?status=active", "queues-tasks-01-active");
    await shot(page, "/queues/low?status=pending", "queues-tasks-02-pending-paused");
    await shot(page, "/queues/critical?status=scheduled", "queues-tasks-03-scheduled");
    await shot(page, "/queues/default?status=retry", "queues-tasks-04-retry");
    await shot(page, "/queues/critical?status=archived", "queues-tasks-05-archived");
    await shot(page, "/queues/default?status=completed", "queues-tasks-06-completed");
    await shot(page, "/queues/default?status=aggregating", "queues-tasks-07-aggregating");
  });

  test("task details via retry row click", async ({ page }) => {
    await page.goto("/queues/default?status=retry");
    await settle(page);
    await page.getByText("sync:export").first().click();
    await settle(page);
    await expect(page.getByText("sync:export").first()).toBeVisible();
    await page.screenshot({ path: `${ASSETS}/task-detail-01-retry-task.png` });
  });

  test("servers, schedulers, redis", async ({ page }) => {
    await page.goto("/servers");
    await settle(page);
    await expect(page.getByText(/active/i).first()).toBeVisible(); // live worker row
    // expand the worker row if collapsible so active task (video:transcode) is visible
    const expander = page.locator("table tbody tr").first().locator("button").first();
    if (await expander.isVisible().catch(() => false)) {
      await expander.click();
      await page.waitForTimeout(400);
    }
    await page.screenshot({ path: `${ASSETS}/servers-workers-01-live.png` });
    await shot(page, "/schedulers", "schedulers-entries-01-list");
    await shot(page, "/redis", "redis-info-01-stats");
  });

  test("settings + dark mode (VRT baseline)", async ({ page }) => {
    await page.goto("/settings");
    await settle(page);
    await page.screenshot({ path: `${ASSETS}/settings-config-01-light.png` });
    await expect(page).toHaveScreenshot("settings-light.png", { fullPage: false });

    await page.locator("#theme-selected").click();
    await page.getByRole("option", { name: "Always" }).click();
    await page.waitForTimeout(600);
    await page.screenshot({ path: `${ASSETS}/settings-config-02-dark.png` });
    await page.goto("/");
    await settle(page);
    await page.screenshot({ path: `${ASSETS}/dashboard-overview-02-dark.png` });
    // restore light theme so reruns start from a known state
    await page.goto("/settings");
    await settle(page);
    await page.locator("#theme-selected").click();
    await page.getByRole("option", { name: "Never" }).click();
  });

  test("metrics page without prometheus (known gap, VRT baseline)", async ({ page }) => {
    await page.goto("/metrics");
    await settle(page);
    await page.screenshot({ path: `${ASSETS}/metrics-gap-01-no-prometheus.png` });
    await expect(page).toHaveScreenshot("metrics-no-prometheus.png", { fullPage: false });
  });
});
