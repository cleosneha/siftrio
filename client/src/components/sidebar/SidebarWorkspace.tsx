"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight, Box } from "lucide-react";
import { cn } from "@/lib/utils";
import { useClients } from "@/hooks/useClients";
import { useProjects } from "@/hooks/useProjects";
import { SidebarClient } from "./SidebarClient";
import type { Client, Workspace } from "@/types";

interface SidebarWorkspaceProps {
  workspace: Workspace;
}

export function SidebarWorkspace({ workspace }: SidebarWorkspaceProps) {
  const pathname = usePathname();
  const [expanded, setExpanded] = useState(true);
  const { data: clientsData } = useClients(workspace.id);
  const clients = clientsData?.data ?? [];

  const isActive = pathname === `/workspaces/${workspace.id}`;

  return (
    <div>
      <div className="flex items-center gap-0">
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center gap-2 rounded-md px-1 py-1.5 text-sm transition-colors hover:bg-accent"
        >
          <ChevronRight
            className={cn(
              "h-3.5 w-3.5 shrink-0 transition-transform",
              expanded && "rotate-90",
            )}
          />
        </button>
        <Link
          href={`/workspaces/${workspace.id}`}
          className={cn(
            "flex flex-1 items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-colors",
            isActive
              ? "bg-accent font-medium text-accent-foreground"
              : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
          )}
        >
          <Box className="h-4 w-4 shrink-0" />
          <span className="truncate">{workspace.name}</span>
        </Link>
      </div>
      {expanded && (
        <div className="ml-4 mt-0.5 space-y-0.5 border-l pl-2">
          {clients.map((client) => (
            <div key={client.id}>
              <SidebarClientWithProjects client={client} />
            </div>
          ))}
          {clients.length === 0 && (
            <p className="px-3 py-1 text-xs text-muted-foreground">
              No clients yet
            </p>
          )}
        </div>
      )}
    </div>
  );
}

function SidebarClientWithProjects({ client }: { client: Client }) {
  const { data: projectsData } = useProjects(client.id);
  const projects = projectsData?.data ?? [];
  return <SidebarClient client={client} projects={projects} />;
}
