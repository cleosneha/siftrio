"use client";

import { FileText, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { Client } from "@/types";

interface ProjectCardProps {
  client: Client;
  onCreateProject: (clientId: string) => void;
}

export function ProjectCard({ client, onCreateProject }: ProjectCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle>{client.name}</CardTitle>
            {client.description && (
              <CardDescription className="line-clamp-2">
                {client.description}
              </CardDescription>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onCreateProject(client.id);
            }}
          >
            <Plus className="h-3 w-3" />
            New Project
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <FileText className="h-3 w-3" />
          <span>
            {client.project_count} project
            {client.project_count !== 1 ? "s" : ""}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
