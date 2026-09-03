import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import sitemap from "@astrojs/sitemap";
import mermaid from "astro-mermaid";
import starlightCatppuccin from "@catppuccin/starlight";
import starlightLinksValidator from "starlight-links-validator";
import starlightLlmsTxt from "starlight-llms-txt";

const SITE = "https://mcgamertime-docs.drmaggi.com";

export default defineConfig({
  site: SITE,
  integrations: [
    mermaid({
      // Enabling autoTheme ensures diagrams match Starlight's dark/light mode
      autoTheme: true,
    }),
    sitemap(),
    starlight({
      title: "MC GamerTime",
      description: "Track board game nights — catalog, results, leaderboard, achievements.",
      plugins: [
        starlightCatppuccin(),
        starlightLinksValidator(),
        starlightLlmsTxt(),
      ],
      lastUpdated: true,
      social: [
        { icon: "github", label: "GitHub", href: "https://github.com/Strandgaard96/mc-gamertime" },
      ],
      favicon: "/favicon.svg",
      head: [
        // Link previews (Discord, Slack, Reddit, X). og:image must be an
        // absolute URL — relative paths are ignored by every scraper.
        { tag: "meta", attrs: { property: "og:image", content: `${SITE}/og.png` } },
        { tag: "meta", attrs: { property: "og:image:width", content: "1200" } },
        { tag: "meta", attrs: { property: "og:image:height", content: "630" } },
        { tag: "meta", attrs: { property: "og:type", content: "website" } },
        { tag: "meta", attrs: { name: "twitter:card", content: "summary_large_image" } },
        { tag: "meta", attrs: { name: "twitter:image", content: `${SITE}/og.png` } },
        // Matches the app's PWA theme colour (web/vite.config.ts).
        { tag: "meta", attrs: { name: "theme-color", content: "#0c1322" } },
        { tag: "link", attrs: { rel: "apple-touch-icon", href: "/apple-touch-icon.png" } },
      ],
      sidebar: [
        {
          label: "Self-Hosting",
          items: [{ autogenerate: { directory: "self-hosting" } }],
        },
        {
          label: "Cloud Deploy",
          items: [{ autogenerate: { directory: "cloud-deploy" } }],
        },
        {
          label: "Contributing",
          items: [{ autogenerate: { directory: "contributing" } }],
        },
      ],
      editLink: {
        baseUrl: "https://github.com/Strandgaard96/mc-gamertime/edit/main/docs-site/",
      },
    }),
  ],
  vite: {
    server: {
      fs: {
        allow: [".."],
      },
    },
  },
});
