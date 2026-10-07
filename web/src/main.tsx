import { QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { Toaster } from "sonner";
import App from "./App";
import { ReloadPrompt } from "./components/ReloadPrompt";
import { createQueryClient } from "./lib/queryClient";
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

const queryClient = createQueryClient();

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
