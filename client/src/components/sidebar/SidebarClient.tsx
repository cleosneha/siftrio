"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight, Folder } from "lucide-react";
import { cn } from "@/lib/utils";
import { SidebarProject } from "./SidebarProject";
import type { Client, Project } from "@/types";

interface SidebarClientProps {
  client: Client;
  projects: Project[];
}

export function SidebarClient({ client, projects }: SidebarClientProps) {
  const pathname = usePathname();
  const [expanded, setExpanded] = useState(true);

  const isClientPage = pathname === `/clients/${client.id}`;

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
          href={`/clients/${client.id}`}
          className={cn(
            "flex flex-1 items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-colors",
            isClientPage
              ? "bg-accent font-medium text-accent-foreground"
              : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
          )}
        >
          <Folder className="h-4 w-4 shrink-0" style={isClientPage ? { color: "#6F84A5" } : undefined} />
          <span className="truncate">{client.name}</span>
        </Link>
      </div>
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
