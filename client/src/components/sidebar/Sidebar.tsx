"use client";

import { useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Plus, Layers, Bot } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent } from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useWorkspaces } from "@/features/workspaces/hooks/useWorkspaces";
import { useAppContext } from "@/lib/app-context";
import { cn } from "@/lib/utils";
import { SidebarWorkspace } from "./SidebarWorkspace";
import type { Workspace } from "@/types";

interface SidebarProps {
  onCreateWorkspace: () => void;
}

export function Sidebar({ onCreateWorkspace }: SidebarProps) {
  const pathname = usePathname();
  const { sidebarOpen, setSidebarOpen } = useAppContext();
  const { data: workspacesData } = useWorkspaces();
  const workspaces: Workspace[] = workspacesData?.data ?? [];
  const isAssistantActive = pathname === "/assistant";

  useEffect(() => {
    setSidebarOpen(false);
  }, [pathname]); // eslint-disable-line react-hooks/exhaustive-deps

  const sidebarContent = (
    <div className="flex h-full flex-col">
      <div className="px-4 py-3">
        <div className="flex items-center justify-between">
          <Link
            href="/dashboard"
            className="flex items-center gap-2 font-medium"
          >
            <Layers className="h-5 w-5" />
            <span className="text-base">Siftrio</span>
          </Link>
        </div>
      </div>

      <Separator />

      <div className="px-3 py-2">
        <Link
          href="/assistant"
          className={cn(
            "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors hover:bg-accent hover:text-accent-foreground",
            isAssistantActive && "bg-accent font-medium text-accent-foreground",
          )}
        >
          <Bot className="h-4 w-4" />
          <span>AI Assistant</span>
        </Link>
      </div>

      <Separator />

      <ScrollArea className="flex-1 px-3 py-2">
        <div className="space-y-1">
          {workspaces.map((workspace) => (
            <SidebarWorkspace key={workspace.id} workspace={workspace} />
          ))}
          {workspaces.length === 0 && (
            <p className="px-3 py-4 text-center text-sm text-muted-foreground">
              No workspaces yet
            </p>
          )}
        </div>
      </ScrollArea>

      <Separator />

      <div className="p-3">
        <Button onClick={onCreateWorkspace} className="w-full">
          <Plus className="h-4 w-4" />
          New Workspace
        </Button>
      </div>
    </div>
  );

  return (
    <>
      <aside className="relative z-50 hidden w-64 shrink-0 border-r md:block">
        {sidebarContent}
      </aside>

      <Sheet open={sidebarOpen} onOpenChange={(o) => setSidebarOpen(o)}>
        <SheetContent side="left" className="w-64 p-0">
          {sidebarContent}
        </SheetContent>
      </Sheet>
    </>
  );
}
