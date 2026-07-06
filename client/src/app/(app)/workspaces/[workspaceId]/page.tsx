"use client";

import dynamic from "next/dynamic";
import { useState } from "react";
import { useParams, notFound } from "next/navigation";
import { Menu, Plus, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ProjectCard } from "@/features/projects/components/ProjectCard";
import { useWorkspace } from "@/features/workspaces/hooks/useWorkspaces";
import { useClients } from "@/features/clients/hooks/useClients";
import { useWorkspaceMembers } from "@/features/members/hooks/useMembers";
import { usePendingInvitations } from "@/features/invitations/hooks/useInvitations";
import { useRemoveWorkspaceMember } from "@/features/members/hooks/useMembers";
import { useAuth } from "@/features/auth/AuthProvider";
import { useAppContext } from "@/lib/app-context";
import { MembersSection } from "@/features/members/MembersSection";

const CreateClientModal = dynamic(
  () =>
    import("@/features/clients/components/CreateClientModal").then(
      (m) => m.CreateClientModal,
    ),
  { ssr: false },
);

const CreateProjectModal = dynamic(
  () =>
    import("@/features/projects/components/CreateProjectModal").then(
      (m) => m.CreateProjectModal,
    ),
  { ssr: false },
);

export default function WorkspacePage() {
  const params = useParams();
  const workspaceId = params.workspaceId as string;
  const { setSidebarOpen } = useAppContext();
  const { user } = useAuth();

  const [showCreateClientModal, setShowCreateClientModal] = useState(false);
  const [showCreateProjectModal, setShowCreateProjectModal] = useState(false);
  const [selectedClientId, setSelectedClientId] = useState<string | null>(null);

  const { data: workspaceData, isLoading: workspaceLoading } = useWorkspace(workspaceId);
  const { data: clientsData } = useClients(workspaceId);
  const { data: membersData, isLoading: membersLoading } = useWorkspaceMembers(workspaceId);
  const { data: invitationsData } = usePendingInvitations("workspace", workspaceId);
  const { mutate: removeMember } = useRemoveWorkspaceMember();

  const workspace = workspaceData?.data;
  const clients = clientsData?.data ?? [];
  const members = membersData?.data ?? [];
  const pendingInvitations = invitationsData?.data ?? [];

  if (!workspaceLoading && !workspace) {
    notFound();
  }

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

      <div className="flex-1 overflow-y-auto p-4 md:p-6">
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
          <div className="mb-8 flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-12 text-center">
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
          <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
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

        <Separator className="mb-6" />

        <MembersSection
          resourceType="workspace"
          resourceId={workspaceId}
          members={members}
          pendingInvitations={pendingInvitations}
          currentUserId={user?.id}
          onRemove={(userId) => removeMember({ workspaceId, userId })}
          isLoading={membersLoading}
        />
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
