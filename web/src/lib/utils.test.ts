import { describe, expect, it } from "vitest";
import { cn, excerpt, formatDate, idFromPk, pluralize, pressable } from "./utils";

describe("cn", () => {
  it("joins class names and drops falsy values", () => {
    const hidden = false;
    expect(cn("a", hidden && "b", undefined, null, "c")).toBe("a c");
  });

  it("resolves tailwind conflicts with the last class winning", () => {
    expect(cn("px-2 py-1", "px-4")).toBe("py-1 px-4");
    expect(cn("text-red-500", "text-blue-500")).toBe("text-blue-500");
  });

  it("supports object and array inputs like clsx", () => {
    expect(cn({ hidden: true, block: false }, ["mt-1", { "mb-1": true }])).toBe("hidden mt-1 mb-1");
  });

  it("keeps the pressable transition-all when merged after transition-colors", () => {
    // Documented in utils.ts: transition-* utilities share one tailwind-merge conflict group.
    const merged = cn("transition-colors", pressable);
    expect(merged).toContain("transition-all");
    expect(merged).not.toContain("transition-colors");
  });
});

describe("pluralize", () => {
  it("uses the singular for exactly one", () => {
    expect(pluralize(1, "session")).toBe("1 session");
  });

  it("appends an s for zero and many", () => {
    expect(pluralize(0, "session")).toBe("0 sessions");
    expect(pluralize(3, "session")).toBe("3 sessions");
  });

  it("uses an explicit plural for irregular words", () => {
    expect(pluralize(2, "victory", "victories")).toBe("2 victories");
    expect(pluralize(1, "victory", "victories")).toBe("1 victory");
  });
});

describe("formatDate", () => {
  it("formats a bare YYYY-MM-DD date in en-US long form", () => {
    expect(formatDate("2026-05-21")).toBe("May 21, 2026");
  });

  it("formats a full ISO timestamp", () => {
    expect(formatDate("2026-01-02T12:00:00")).toBe("January 2, 2026");
  });

  it("treats a bare date as local midnight so it never rolls back a day", () => {
    // A naive `new Date("2026-05-21")` parses as UTC midnight, which in a
    // negative-offset zone would render as May 20.
    expect(formatDate("2026-12-31")).toBe("December 31, 2026");
    expect(formatDate("2026-01-01")).toBe("January 1, 2026");
  });
});

describe("idFromPk", () => {
  it("strips a PREFIX# from a prefixed key", () => {
    expect(idFromPk("PLAYER#01HXYZ")).toBe("01HXYZ");
    expect(idFromPk("GAME#abc")).toBe("abc");
  });

  it("returns a bare ULID or username unchanged", () => {
    expect(idFromPk("01HXYZ")).toBe("01HXYZ");
    expect(idFromPk("alice")).toBe("alice");
  });
});

describe("excerpt", () => {
  it("strips HTML tags and trims surrounding whitespace", () => {
    expect(excerpt("<p>  Hello <strong>world</strong>  </p>")).toBe("Hello world");
  });

  it("returns short text without an ellipsis", () => {
    expect(excerpt("<p>short</p>", 10)).toBe("short");
  });

  it("truncates long text at the limit and appends an ellipsis", () => {
    const out = excerpt("<p>abcdefghijklmnopqrstuvwxyz</p>", 10);
    expect(out).toBe("abcdefghij…");
  });

  it("trims trailing whitespace before the ellipsis", () => {
    expect(excerpt("hello world again", 6)).toBe("hello…");
  });

  it("defaults to 150 characters", () => {
    const long = "x".repeat(200);
    expect(excerpt(long)).toBe(`${"x".repeat(150)}…`);
    expect(excerpt("x".repeat(150))).toBe("x".repeat(150));
  });
});
