"use client";

import {
  createContext,
  useContext,
  useCallback,
  type ReactNode,
} from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { authService } from "./auth.service";
import type { User } from "./auth.types";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["auth", "me"],
    queryFn: authService.me,
    staleTime: Infinity,
  });

  const user = data?.success && data.data ? data.data : null;

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } finally {
      queryClient.setQueryData(["auth", "me"], {
        success: false,
        data: null,
      });
    }
  }, [queryClient]);

  return (
    <AuthContext.Provider value={{ user, loading: isLoading, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
