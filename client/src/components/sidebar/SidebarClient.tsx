"use client";

import { useState } from "react";
import { ChevronRight, Folder } from "lucide-react";
import { cn } from "@/lib/utils";
import { SidebarProject } from "./SidebarProject";
import type { Client, Project } from "@/types";

interface SidebarClientProps {
  client: Client;
  projects: Project[];
}

export function SidebarClient({ client, projects }: SidebarClientProps) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div>
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 rounded-md px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
      >
        <ChevronRight
          className={cn(
            "h-3.5 w-3.5 shrink-0 transition-transform",
            expanded && "rotate-90",
          )}
        />
        <Folder className="h-4 w-4 shrink-0" />
        <span className="truncate">{client.name}</span>
      </button>
      {expanded && (
        <div className="ml-4 mt-0.5 space-y-0.5 border-l pl-2">
          {projects.map((project) => (
            <SidebarProject key={project.id} project={project} />
          ))}
          {projects.length === 0 && (
            <p className="px-3 py-1 text-xs text-muted-foreground">
              No projects yet
            </p>
          )}
        </div>
      )}
    </div>
  );
}
