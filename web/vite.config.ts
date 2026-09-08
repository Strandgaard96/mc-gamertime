import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'prompt',
      includeAssets: ['favicon.svg', 'apple-touch-icon.png'],
      manifest: {
        name: 'MC GamerTime',
        short_name: 'GamerTime',
        description: 'Track board game nights — catalog, results, leaderboard',
        display: 'standalone',
        start_url: '/',
        theme_color: '#0c1322',
        background_color: '#0c1322',
        icons: [
          { src: '/pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: '/pwa-512x512.png', sizes: '512x512', type: 'image/png' },
          {
            src: '/pwa-maskable-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable',
          },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,woff2}'],
        // API calls and S3-served user content must never resolve to index.html
        navigateFallbackDenylist: [/^\/api\//, /^\/(blog-images|avatars|exports)\//],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/cf\.geekdo-images\.com\/.*/i,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'bgg-images',
              expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 30 },
            },
          },
          {
            urlPattern: ({ url, sameOrigin }) =>
              sameOrigin &&
              (url.pathname.startsWith('/blog-images/') ||
                url.pathname.startsWith('/avatars/')),
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'user-images',
              expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 30 },
            },
          },
        ],
      },
    }),
  ],
  base: '/',
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
