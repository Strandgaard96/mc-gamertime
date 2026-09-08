import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { Toaster } from "sonner";
import App from "./App";
import { ReloadPrompt } from "./components/ReloadPrompt";
import "./styles/globals.css";
import "@fontsource/space-grotesk/400.css";
import "@fontsource/space-grotesk/500.css";
import "@fontsource/space-grotesk/600.css";
import "@fontsource/space-grotesk/700.css";
import { syncThemeColor } from "./lib/themeColor";
import { DEFAULT_THEME, THEMES } from "./lib/themes";

const saved = localStorage.getItem("mc-theme") ?? DEFAULT_THEME;
const validTheme = THEMES.some((t) => t.id === saved) ? saved : DEFAULT_THEME;
document.documentElement.dataset.theme = validTheme;

// Wait one frame so the stylesheet's theme variables are applied first
requestAnimationFrame(syncThemeColor);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 2,
      // A 4xx is an answer, not a blip. Retrying one just multiplies the
      // console noise — six failed /recommended calls on the logged-out
      // landing page when PUBLIC_RECOMMENDED_ENABLED is unset, for instance.
      retry: (failureCount, error) => {
        const status = (error as { status?: number }).status;
        if (status !== undefined && status >= 400 && status < 500) return false;
        return failureCount < 3;
      },
    },
  },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <App />
        <Toaster
          theme="dark"
          position="bottom-right"
          richColors
          // Clear of the fixed mobile tab bar, which the toasts covered.
          offset={{ bottom: "calc(4.5rem + env(safe-area-inset-bottom))" }}
        />
        <ReloadPrompt />
      </QueryClientProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
