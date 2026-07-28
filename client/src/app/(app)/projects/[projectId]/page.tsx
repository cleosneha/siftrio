"use client";

import { useParams, notFound } from "next/navigation";
import { useState } from "react";
import { Menu, ArrowLeft, Plus } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useProject } from "@/features/projects/hooks/useProjects";
import { useMeetingsByProject } from "@/features/meetings/hooks/useMeetings";
import { useProjectMembers } from "@/features/members/hooks/useMembers";
import { usePendingInvitations } from "@/features/invitations/hooks/useInvitations";
import { useRemoveProjectMember } from "@/features/members/hooks/useMembers";
import { useAuth } from "@/features/auth/AuthProvider";
import { useAppContext } from "@/lib/app-context";
import { CreateMeetingModal } from "@/features/meetings/components/CreateMeetingModal";
import { MeetingsListModal } from "@/features/meetings/components/MeetingsListModal";
import { KnowledgeSection } from "@/features/knowledge/KnowledgeSection";
import { MembersSection } from "@/features/members/MembersSection";
import { JiraIntegrationSection } from "@/features/jira/components/JiraIntegrationSection";

export default function ProjectPage() {
  const params = useParams();
  const projectId = params.projectId as string;
  const { setSidebarOpen } = useAppContext();
  const { user } = useAuth();
  const [showCreateMeeting, setShowCreateMeeting] = useState(false);
  const [showMeetingsList, setShowMeetingsList] = useState(false);

  const { data: projectData, isLoading: projectLoading } = useProject(projectId);
  const { data: meetingsData } = useMeetingsByProject(projectId);
  const { data: membersData, isLoading: membersLoading } = useProjectMembers(projectId);
  const { data: invitationsData } = usePendingInvitations("project", projectId);
  const { mutate: removeMember } = useRemoveProjectMember();

  const project = projectData?.data;
  const members = membersData?.data ?? [];
  const pendingInvitations = invitationsData?.data ?? [];

  if (!projectLoading && !project) {
    notFound();
  }

  return (
    <>
      <header className="flex items-center gap-3 px-4 py-3 md:px-6">
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
        <div className="flex flex-1 items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold">
              {project?.name ?? "Loading..."}
            </h1>
            {project?.description && (
              <p className="text-sm text-muted-foreground">
                {project.description}
              </p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              className="bg-elevated text-foreground hover:bg-hover-surface"
              onClick={() => setShowMeetingsList(true)}
            >
              Show Meetings
            </Button>
            <Button onClick={() => setShowCreateMeeting(true)}>
              <Plus className="h-4 w-4" />
              New Meeting
            </Button>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1 overflow-y-auto p-4 md:p-6">
          <div className="mb-6">
            <h2 className="mb-4 text-lg font-medium">Knowledge</h2>
            <KnowledgeSection projectId={projectId} />
          </div>

          <Separator className="mb-6" />

          <div className="mb-6">
            <JiraIntegrationSection projectId={projectId} clientId={project?.client_id ?? ""} />
          </div>

          <Separator className="mb-6" />

          <MembersSection
            resourceType="project"
            resourceId={projectId}
            members={members}
            pendingInvitations={pendingInvitations}
            currentUserId={user?.id}
            onRemove={(userId) => removeMember({ projectId, userId })}
            isLoading={membersLoading}
          />
        </div>
      </div>

      <CreateMeetingModal
        open={showCreateMeeting}
        onClose={() => setShowCreateMeeting(false)}
        clientId={project?.client_id ?? ""}
        defaultProjectId={projectId}
      />

      <MeetingsListModal
        open={showMeetingsList}
        onClose={() => setShowMeetingsList(false)}
        meetings={meetingsData?.data ?? []}
      />
    </>
  );
}
