import { beforeEach, describe, expect, it } from "vitest";
import parseFlagsUnderWindow from "./parseFlags";

// The server injects FLAG_* strings into index.html via Go templates
// (custom "/[[" "]]" delimiters). parseFlagsUnderWindow must fall back
// safely when an action was left unevaluated (e.g. opened without server).
describe("parseFlagsUnderWindow", () => {
  beforeEach(() => {
    // reset window flags between cases
    (window as any).FLAG_ROOT_PATH = undefined;
    (window as any).FLAG_PROMETHEUS_SERVER_ADDRESS = undefined;
    (window as any).FLAG_READ_ONLY = undefined;
  });

  it("parses server-evaluated flags", () => {
    window.FLAG_ROOT_PATH = "/monitoring";
    window.FLAG_PROMETHEUS_SERVER_ADDRESS = "http://localhost:9090";
    window.FLAG_READ_ONLY = "true";
    parseFlagsUnderWindow();
    expect(window.ROOT_PATH).toBe("/monitoring");
    expect(window.PROMETHEUS_SERVER_ADDRESS).toBe("http://localhost:9090");
    expect(window.READ_ONLY).toBe(true);
  });

  it("falls back when go-template actions were not evaluated", () => {
    window.FLAG_ROOT_PATH = "/[[.RootPath]]"; // root path is used verbatim by design
    window.FLAG_PROMETHEUS_SERVER_ADDRESS = "/[[.PrometheusAddr]]";
    window.FLAG_READ_ONLY = "/[[.ReadOnly]]";
    parseFlagsUnderWindow();
    expect(window.PROMETHEUS_SERVER_ADDRESS).toBe("");
    expect(window.READ_ONLY).toBe(false);
  });

  it("falls back when flags are undefined", () => {
    parseFlagsUnderWindow();
    expect(window.ROOT_PATH).toBe("");
    expect(window.PROMETHEUS_SERVER_ADDRESS).toBe("");
    expect(window.READ_ONLY).toBe(false);
  });
});
