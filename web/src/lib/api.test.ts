import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { checkHealth, deleteGame, getGames, login } from "./api";
import { navigation, setClearAuth } from "./navigation";

function mockResponse(
  status: number,
  body: string | null = null,
  headers: Record<string, string> = {},
): Response {
  return new Response(body, { status, headers });
}

const fetchMock = vi.fn<typeof fetch>();

beforeEach(() => {
  vi.stubGlobal("fetch", fetchMock);
  sessionStorage.clear();
  window.history.replaceState({}, "", "/games");
});

afterEach(() => {
  vi.unstubAllGlobals();
  fetchMock.mockReset();
  setClearAuth(() => {});
});

describe("apiFetch", () => {
  it("prefixes the path with /api and parses JSON on success", async () => {
    fetchMock.mockResolvedValue(
      mockResponse(200, JSON.stringify([{ pk: "g1", name: "Catan" }]), {
        "Content-Type": "application/json",
      }),
    );

    const games = await getGames();

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe("/api/games");
    expect(games).toEqual([{ pk: "g1", name: "Catan" }]);
  });

  it("forwards method, headers and body to fetch", async () => {
    fetchMock.mockResolvedValue(
      mockResponse(200, JSON.stringify({ username: "alice", role: "admin" })),
    );

    await login("alice", "secret");

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/auth/login");
    expect(init?.method).toBe("POST");
    expect(init?.headers).toEqual({ "Content-Type": "application/json" });
    expect(JSON.parse(init?.body as string)).toEqual({ username: "alice", password: "secret" });
  });

  it("resolves undefined on a 204 without reading a body", async () => {
    fetchMock.mockResolvedValue(mockResponse(204));

    await expect(deleteGame("g1")).resolves.toBeUndefined();
    expect(fetchMock.mock.calls[0][0]).toBe("/api/games/g1");
    expect(fetchMock.mock.calls[0][1]?.method).toBe("DELETE");
  });

  it("on 401 stores the current path, clears auth and throws an AuthError", async () => {
    const clearAuth = vi.fn();
    setClearAuth(clearAuth);
    fetchMock.mockResolvedValue(mockResponse(401, JSON.stringify({ detail: "nope" })));

    await expect(getGames()).rejects.toMatchObject({ status: 401, message: "Unauthorized" });

    expect(sessionStorage.getItem("_expiredRedirect")).toBe("/games");
    expect(clearAuth).toHaveBeenCalledTimes(1);
    expect(navigation.clearAuth).toBe(clearAuth);
  });

  it("on 401 from the login page does not overwrite the redirect target", async () => {
    window.history.replaceState({}, "", "/login");
    sessionStorage.setItem("_expiredRedirect", "/players");
    fetchMock.mockResolvedValue(mockResponse(401));

    await expect(login("alice", "wrong")).rejects.toMatchObject({ status: 401 });

    expect(sessionStorage.getItem("_expiredRedirect")).toBe("/players");
  });

  it("throws the server's detail message on a non-2xx JSON error", async () => {
    fetchMock.mockResolvedValue(
      mockResponse(422, JSON.stringify({ detail: "Variables do not match game config" })),
    );

    await expect(getGames()).rejects.toThrow("Variables do not match game config");
  });

  it("falls back to a generic message when detail is not a string", async () => {
    fetchMock.mockResolvedValue(
      mockResponse(422, JSON.stringify({ detail: [{ loc: ["body"], msg: "bad" }] })),
    );

    await expect(getGames()).rejects.toThrow("API error 422");
  });

  it("uses the raw body when the error response is not JSON", async () => {
    fetchMock.mockResolvedValue(mockResponse(502, "Bad Gateway"));

    await expect(getGames()).rejects.toThrow("Bad Gateway");
  });

  it("uses a generic message when the error body is empty", async () => {
    fetchMock.mockResolvedValue(mockResponse(500, ""));

    await expect(getGames()).rejects.toThrow("API error 500");
  });

  it("attaches status and parsed Retry-After on a 429", async () => {
    fetchMock.mockResolvedValue(
      mockResponse(429, JSON.stringify({ detail: "Too many requests" }), {
        "Retry-After": "30",
      }),
    );

    await expect(login("alice", "x")).rejects.toMatchObject({
      status: 429,
      retryAfter: 30,
      message: "Too many requests",
    });
  });

  it("sets retryAfter to null when the 429 has no usable Retry-After header", async () => {
    fetchMock.mockResolvedValue(mockResponse(429, JSON.stringify({ detail: "slow down" })));

    await expect(login("alice", "x")).rejects.toMatchObject({ status: 429, retryAfter: null });
  });
});

describe("checkHealth", () => {
  it("returns true when /api/health responds ok", async () => {
    fetchMock.mockResolvedValue(mockResponse(200, "ok"));

    await expect(checkHealth()).resolves.toBe(true);
    expect(fetchMock.mock.calls[0][0]).toBe("/api/health");
  });

  it("returns false on a non-ok status", async () => {
    fetchMock.mockResolvedValue(mockResponse(503));

    await expect(checkHealth()).resolves.toBe(false);
  });

  it("returns false when fetch itself rejects", async () => {
    fetchMock.mockRejectedValue(new TypeError("Failed to fetch"));

    await expect(checkHealth()).resolves.toBe(false);
  });
});
