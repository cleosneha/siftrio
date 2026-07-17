"use client";

import { useState, type ReactNode } from "react";
import dynamic from "next/dynamic";
import { Toaster } from "@/components/ui/sonner";
import { AppProvider } from "@/lib/app-context";
import { ProtectedRoute } from "@/features/auth/ProtectedRoute";
import { MeetingsDrawerProvider } from "@/features/meetings/meetings-drawer-store";

const Sidebar = dynamic(
  () => import("@/components/sidebar/Sidebar").then((m) => m.Sidebar),
  { ssr: false },
);

const CreateWorkspaceModal = dynamic(
  () =>
    import("@/features/workspaces/components/CreateWorkspaceModal").then(
      (m) => m.CreateWorkspaceModal,
    ),
  { ssr: false },
);

const MeetingsDrawer = dynamic(
  () =>
    import("@/features/meetings/MeetingsDrawer").then((m) => m.MeetingsDrawer),
  { ssr: false },
);

export default function AppLayout({ children }: { children: ReactNode }) {
  const [showCreateModal, setShowCreateModal] = useState(false);

  return (
    <ProtectedRoute>
      <AppProvider onOpenCreateWorkspace={() => setShowCreateModal(true)}>
        <MeetingsDrawerProvider>
          <div className="flex h-[calc(100vh-3.5rem)]">
            <Sidebar onCreateWorkspace={() => setShowCreateModal(true)} />
            <main className="flex min-h-0 flex-1 flex-col overflow-y-auto">
              {children}
            </main>
            <CreateWorkspaceModal
              open={showCreateModal}
              onClose={() => setShowCreateModal(false)}
            />
            <Toaster />
          </div>
          <MeetingsDrawer />
        </MeetingsDrawerProvider>
      </AppProvider>
    </ProtectedRoute>
  );
}
