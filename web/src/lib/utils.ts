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

/** Strip HTML tags from a string */
function stripHtml(html: string): string {
  return html.replace(/<[^>]*>/g, "");
}

/** First n characters of plain text from HTML */
export function excerpt(html: string, length = 150): string {
  const plain = stripHtml(html).trim();
  return plain.length <= length ? plain : `${plain.slice(0, length).trimEnd()}…`;
}
