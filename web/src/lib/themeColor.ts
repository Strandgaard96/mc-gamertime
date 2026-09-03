/**
 * Sync the <meta name="theme-color"> tag to the active theme's --background.
 * Controls the status-bar / window-chrome color in installed PWAs.
 */
export function syncThemeColor() {
  const bg = getComputedStyle(document.documentElement).getPropertyValue("--background").trim();
  if (!bg) return;
  let meta = document.querySelector<HTMLMetaElement>('meta[name="theme-color"]');
  if (!meta) {
    meta = document.createElement("meta");
    meta.name = "theme-color";
    document.head.appendChild(meta);
  }
  meta.content = `hsl(${bg})`;
}
