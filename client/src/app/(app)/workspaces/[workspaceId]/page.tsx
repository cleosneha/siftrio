"use client";

import dynamic from "next/dynamic";
import { useState } from "react";
import { useParams } from "next/navigation";
import { Menu, Plus, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ProjectCard } from "@/components/project/ProjectCard";
import { useWorkspace } from "@/hooks/useWorkspaces";
import { useClients } from "@/hooks/useClients";
import { useAppContext } from "@/lib/app-context";

const CreateClientModal = dynamic(
  () =>
    import("@/components/workspace/CreateClientModal").then(
      (m) => m.CreateClientModal,
    ),
  { ssr: false },
);

const CreateProjectModal = dynamic(
  () =>
    import("@/components/project/CreateProjectModal").then(
      (m) => m.CreateProjectModal,
    ),
  { ssr: false },
);

export default function WorkspacePage() {
  const params = useParams();
  const workspaceId = params.workspaceId as string;
  const { setSidebarOpen } = useAppContext();

  const [showCreateClientModal, setShowCreateClientModal] = useState(false);
  const [showCreateProjectModal, setShowCreateProjectModal] = useState(false);
  const [selectedClientId, setSelectedClientId] = useState<string | null>(null);

  const { data: workspaceData } = useWorkspace(workspaceId);
  const { data: clientsData } = useClients(workspaceId);

  const workspace = workspaceData?.data;
  const clients = clientsData?.data ?? [];

  return (
    <>
      <header className="flex items-center gap-3 border-b px-4 py-3 md:px-6">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setSidebarOpen(true)}
          className="md:hidden"
        >
          <Menu className="h-5 w-5" />
        </Button>
        <Link href="/dashboard">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div>
          <h1 className="text-xl font-semibold">
            {workspace?.name ?? "Loading..."}
          </h1>
          {workspace?.description && (
            <p className="text-sm text-muted-foreground">
              {workspace.description}
            </p>
          )}
        </div>
      </header>

      <div className="flex-1 p-4 md:p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-medium">Clients</h2>
            <p className="text-sm text-muted-foreground">
              {clients.length} client{clients.length !== 1 ? "s" : ""}
            </p>
          </div>
          <Button onClick={() => setShowCreateClientModal(true)}>
            <Plus className="h-4 w-4" />
            New Client
          </Button>
        </div>

        {clients.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-12 text-center">
            <h3 className="mb-2 text-lg font-medium">No clients yet</h3>
            <p className="mb-4 text-sm text-muted-foreground">
              Create a client to start organizing projects
            </p>
            <Button onClick={() => setShowCreateClientModal(true)}>
              <Plus className="h-4 w-4" />
              Create Client
            </Button>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {clients.map((client) => (
              <ProjectCard
                key={client.id}
                client={client}
                onCreateProject={(clientId) => {
                  setSelectedClientId(clientId);
                  setShowCreateProjectModal(true);
                }}
              />
            ))}
          </div>
        )}
      </div>

      <CreateClientModal
        open={showCreateClientModal}
        onClose={() => setShowCreateClientModal(false)}
        workspaceId={workspaceId}
      />
      <CreateProjectModal
        open={showCreateProjectModal}
        onClose={() => {
          setShowCreateProjectModal(false);
          setSelectedClientId(null);
        }}
        clientId={selectedClientId ?? ""}
      />
    </>
  );
}
