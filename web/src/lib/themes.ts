export interface Theme {
  id: string;
  label: string;
  primaryHex: string;
}

export const THEMES: Theme[] = [
  { id: "dark-gold", label: "Gold", primaryHex: "#f5a623" },
  { id: "midnight", label: "Violet", primaryHex: "#818cf8" },
  { id: "neon-tokyo", label: "Neon Tokyo", primaryHex: "#22d3ee" },
  { id: "obsidian", label: "Obsidian", primaryHex: "#38bdf8" },
  { id: "evergreen", label: "Evergreen", primaryHex: "#4ade80" },
  { id: "dracula", label: "Dracula", primaryHex: "#f87171" },
  { id: "nebula", label: "Nebula", primaryHex: "#c084fc" },
];

export const DEFAULT_THEME = "dracula";
