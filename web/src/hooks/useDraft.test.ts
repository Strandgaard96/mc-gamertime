import { renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useDraft } from "./useDraft";

const KEY = "post-draft:test";

// Node >= 22 ships its own `localStorage` global that is `undefined` unless
// `--localstorage-file` is passed, and it shadows jsdom's implementation. Stub
// a minimal in-memory Storage so the hook exercises real get/set/remove paths.
function memoryStorage() {
  const store = new Map<string, string>();
  return {
    getItem: (k: string) => store.get(k) ?? null,
    setItem: (k: string, v: string) => void store.set(k, String(v)),
    removeItem: (k: string) => void store.delete(k),
    clear: () => store.clear(),
  };
}

let storage: ReturnType<typeof memoryStorage>;

beforeEach(() => {
  storage = memoryStorage();
  vi.stubGlobal("localStorage", storage);
  vi.useFakeTimers();
  vi.setSystemTime(new Date("2026-05-21T10:30:00.000Z"));
});

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

describe("useDraft", () => {
  it("returns null when nothing is stored", () => {
    const { result } = renderHook(() => useDraft(KEY));
    expect(result.current.load()).toBeNull();
  });

  it("round-trips a draft and stamps savedAt with the current time", () => {
    const { result } = renderHook(() => useDraft(KEY));

    result.current.save({ title: "Night 1", content: "<p>hi</p>", sessionPk: "01ABC" });

    expect(result.current.load()).toEqual({
      title: "Night 1",
      content: "<p>hi</p>",
      sessionPk: "01ABC",
      savedAt: "2026-05-21T10:30:00.000Z",
    });
  });

  it("isolates drafts by key", () => {
    const a = renderHook(() => useDraft("draft:a")).result.current;
    const b = renderHook(() => useDraft("draft:b")).result.current;

    a.save({ title: "A", content: "", sessionPk: "" });

    expect(a.load()?.title).toBe("A");
    expect(b.load()).toBeNull();
  });

  it("clear removes the stored draft", () => {
    const { result } = renderHook(() => useDraft(KEY));
    result.current.save({ title: "x", content: "", sessionPk: "" });

    result.current.clear();

    expect(result.current.load()).toBeNull();
    expect(storage.getItem(KEY)).toBeNull();
  });

  it("returns null instead of throwing on corrupt JSON", () => {
    storage.setItem(KEY, "{not json");
    const { result } = renderHook(() => useDraft(KEY));

    expect(result.current.load()).toBeNull();
  });

  it("swallows storage errors on save", () => {
    storage.setItem = () => {
      throw new DOMException("quota", "QuotaExceededError");
    };
    const { result } = renderHook(() => useDraft(KEY));

    expect(() => result.current.save({ title: "x", content: "", sessionPk: "" })).not.toThrow();
    expect(result.current.load()).toBeNull();
  });
});
