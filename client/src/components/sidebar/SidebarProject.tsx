"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { FileText } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Project } from "@/types";

interface SidebarProjectProps {
  project: Project;
}

export function SidebarProject({ project }: SidebarProjectProps) {
  const pathname = usePathname();
  const isActive = pathname === `/projects/${project.id}`;

  return (
    <Link
      href={`/projects/${project.id}`}
      className={cn(
        "flex items-center gap-2 rounded-md px-3 py-1.5 text-sm transition-colors",
        isActive
          ? "bg-accent font-medium text-accent-foreground"
          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
      )}
    >
      <FileText className="h-3.5 w-3.5 shrink-0" style={isActive ? { color: "#5E8B6D" } : undefined} />
      <span className="truncate">{project.name}</span>
    </Link>
  );
}
