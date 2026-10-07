import { useQueryClient } from "@tanstack/react-query";
import { createContext, type ReactNode, useContext, useEffect, useRef, useState } from "react";
import { logout as apiLogout, getCurrentUser } from "./api";
import type { AuthUser } from "./types";

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  setUser: (user: AuthUser | null) => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const queryClient = useQueryClient();
  const previousUser = useRef<string | null>(null);

  // The cache holds per-user data (isFavorited, the notification inbox). When
  // a session ends, by logout or by a 401 clearing the user, drop all of it so
  // the next account on this browser never sees the previous one's data.
  useEffect(() => {
    const current = user?.sub ?? null;
    if (previousUser.current !== null && previousUser.current !== current) {
      queryClient.clear();
    }
    previousUser.current = current;
  }, [user, queryClient]);

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  async function logout(): Promise<void> {
    try {
      await apiLogout();
    } catch {
      /* ignore */
    }
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, setUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
