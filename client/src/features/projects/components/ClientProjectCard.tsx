"use client";

import Link from "next/link";
import { ProjectCard } from "@/features/projects/components/ProjectCard";
import { useMyRole } from "@/features/members/hooks/useMembers";
import { canCreateResource } from "@/types";
import type { Client } from "@/types";

interface ClientProjectCardProps {
  client: Client;
  onCreateProject: (clientId: string) => void;
}

export function ClientProjectCard({
  client,
  onCreateProject,
}: ClientProjectCardProps) {
  const { data: role } = useMyRole("client", client.id);
  return (
    <Link href={`/clients/${client.id}`}>
      <ProjectCard
        client={client}
        onCreateProject={onCreateProject}
        canCreateProject={canCreateResource(role)}
      />
    </Link>
  );
}
