import axios from "axios";
import queryString from "query-string";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { getMetrics, listActiveTasks } from "./api";

vi.mock("axios", () => ({ default: vi.fn() }));

describe("API query serialization after dependency upgrades", () => {
  beforeEach(() => {
    vi.mocked(axios).mockReset();
    vi.mocked(axios).mockResolvedValue({ data: {} });
    window.ROOT_PATH = "/monitoring";
  });

  it("keeps pagination numbers and omits undefined values", async () => {
    await listActiveTasks("default", { page: 2, size: undefined });
    expect(axios).toHaveBeenCalledWith({
      method: "get",
      url: "http://localhost:8080/monitoring/api/queues/default/active_tasks?page=2",
    });
  });

  it("encodes queue names and preserves metrics parameters", async () => {
    await getMetrics(123, 3600, ["critical jobs", "背景"]);
    expect(axios).toHaveBeenCalledWith({
      method: "get",
      url: "http://localhost:8080/monitoring/api/metrics?duration=3600&endtime=123&queues=critical%20jobs%2C%E8%83%8C%E6%99%AF",
    });
  });

  it("omits the queues parameter when no queue is selected", async () => {
    await getMetrics(123, 3600, []);
    expect(axios).toHaveBeenCalledWith({
      method: "get",
      url: "http://localhost:8080/monitoring/api/metrics?duration=3600&endtime=123",
    });
  });

  it("loads the ESM decoder and decodes escaped query values", () => {
    expect(queryString.parse("queues=critical%20jobs%2C%E8%83%8C%E6%99%AF"))
      .toEqual({ queues: "critical jobs,背景" });
  });
});
