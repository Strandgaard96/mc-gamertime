import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { getGames } from "./api";
import { shouldRetryQuery } from "./queryClient";

const fetchMock = vi.fn<typeof fetch>();

beforeEach(() => vi.stubGlobal("fetch", fetchMock));
afterEach(() => {
  vi.unstubAllGlobals();
  fetchMock.mockReset();
});

async function errorFromStatus(status: number): Promise<unknown> {
  fetchMock.mockResolvedValue(new Response(JSON.stringify({ detail: "nope" }), { status }));
  return getGames().catch((e: unknown) => e);
}

describe("shouldRetryQuery", () => {
  it.each([403, 404, 422])("does not retry a %i from the API", async (status) => {
    expect(shouldRetryQuery(0, await errorFromStatus(status))).toBe(false);
  });

  it("retries a 5xx up to three times", async () => {
    const err = await errorFromStatus(503);
    expect(shouldRetryQuery(0, err)).toBe(true);
    expect(shouldRetryQuery(3, err)).toBe(false);
  });

  it("retries a network failure", () => {
    expect(shouldRetryQuery(0, new TypeError("Failed to fetch"))).toBe(true);
  });
});
