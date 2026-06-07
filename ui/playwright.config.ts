import { defineConfig } from "@playwright/test";

// Manual-screenshot / smoke E2E config.
// The asynqmon server + seeded demo data must already be running under a
// registry-governed allocation (see docs/MANUAL_GENERATION_GUIDE.md).
export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  use: {
    baseURL: process.env.ASYNQMON_BASE_URL || "http://localhost:28090",
    viewport: { width: 1440, height: 900 },
    locale: "en-US",
    timezoneId: "UTC",
  },
  expect: {
    toHaveScreenshot: { maxDiffPixelRatio: 0.02, animations: "disabled" },
  },
  reporter: [["list"]],
});
