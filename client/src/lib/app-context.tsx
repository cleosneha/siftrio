"use client";

import { createContext, useContext, useState, type ReactNode } from "react";

interface AppContextType {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  setShowCreateWorkspace: (open: boolean) => void;
}

const AppContext = createContext<AppContextType | null>(null);

export function AppProvider({
  children,
  onOpenCreateWorkspace,
}: {
  children: ReactNode;
  onOpenCreateWorkspace: () => void;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <AppContext.Provider
      value={{
        sidebarOpen,
        setSidebarOpen,
        setShowCreateWorkspace: onOpenCreateWorkspace,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppContext must be used within AppProvider");
  return ctx;
}
