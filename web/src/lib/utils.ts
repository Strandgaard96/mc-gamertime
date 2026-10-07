import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Tap/press feedback. Use transition-all (not transition-transform) — tailwind-merge
// treats all transition-* utilities as one conflict group, so a narrower class here
// would silently drop an element's existing transition-colors/transition-all.
export const pressable = "motion-safe:active:scale-[0.97] transition-all duration-100";

/** "1 session" / "3 sessions" — pass an explicit plural for irregular words */
export function pluralize(
  count: number,
  singular: string,
  plural: string = `${singular}s`,
): string {
  return `${count} ${count === 1 ? singular : plural}`;
}

export function formatDate(iso: string): string {
  const d = iso.includes("T") ? new Date(iso) : new Date(`${iso}T00:00:00`);
  return d.toLocaleDateString("en-US", { day: "numeric", month: "long", year: "numeric" });
}

// Extract player ULID from pk "PLAYER#<ulid>" or return pk if no prefix
export function idFromPk(pk: string): string {
  return pk.includes("#") ? pk.split("#")[1] : pk;
}

/**
 * Fills for letter placeholders (avatars, game stamps). Every entry keeps white text
 * at ≥ 4.7:1 — the old amber/emerald/cyan -600 shades were 3.2–3.8:1.
 */
export const PLACEHOLDER_COLORS = [
  "#e11d48",
  "#7c3aed",
  "#2563eb",
  "#0e7490",
  "#047857",
  "#b45309",
  "#c2410c",
  "#be185d",
];

/** Stable placeholder colour for a name — hashes the whole string, not just its first letter. */
export function colorForName(name: string): string {
  let hash = 0;
  for (const ch of name) hash = (hash * 31 + ch.charCodeAt(0)) | 0;
  return PLACEHOLDER_COLORS[Math.abs(hash) % PLACEHOLDER_COLORS.length];
}

/** Strip HTML tags from a string */
function stripHtml(html: string): string {
  // Block-level boundaries become spaces so "<p>a.</p><p>b</p>" reads "a. b", not "a.b".
  return html
    .replace(/<\/(p|div|li|h[1-6]|blockquote)>|<br\s*\/?>/gi, " ")
    .replace(/<[^>]*>/g, "")
    .replace(/\s+/g, " ");
}

/** First n characters of plain text from HTML */
export function excerpt(html: string, length = 150): string {
  const plain = stripHtml(html).trim();
  return plain.length <= length ? plain : `${plain.slice(0, length).trimEnd()}…`;
}
