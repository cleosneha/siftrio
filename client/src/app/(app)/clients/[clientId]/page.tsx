"use client";

import { useParams, notFound } from "next/navigation";
import { useState } from "react";
import { Menu, ArrowLeft, Plus } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useClient } from "@/features/clients/hooks/useClients";
import { useProjects } from "@/features/projects/hooks/useProjects";
import { useMiscellaneousMeetings } from "@/features/meetings/hooks/useMeetings";
import { useClientMembers } from "@/features/members/hooks/useMembers";
import { usePendingInvitations } from "@/features/invitations/hooks/useInvitations";
import { useRemoveClientMember } from "@/features/members/hooks/useMembers";
import { useAuth } from "@/features/auth/AuthProvider";
import { useAppContext } from "@/lib/app-context";
import { CreateProjectModal } from "@/features/projects/components/CreateProjectModal";
import { CreateMeetingModal } from "@/features/meetings/components/CreateMeetingModal";
import { MembersSection } from "@/features/members/MembersSection";

export default function ClientPage() {
  const params = useParams();
  const clientId = params.clientId as string;
  const { setSidebarOpen } = useAppContext();
  const { user } = useAuth();
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [showCreateMeeting, setShowCreateMeeting] = useState(false);

  const { data: clientData, isLoading: clientLoading } = useClient(clientId);
  const { data: projectsData } = useProjects(clientId);
  const { data: meetingsData } = useMiscellaneousMeetings(clientId);
  const { data: membersData, isLoading: membersLoading } = useClientMembers(clientId);
  const { data: invitationsData } = usePendingInvitations("client", clientId);
  const { mutate: removeMember } = useRemoveClientMember();

  const client = clientData?.data;
  const projects = projectsData?.data ?? [];
  const meetings = meetingsData?.data ?? [];
  const members = membersData?.data ?? [];
  const pendingInvitations = invitationsData?.data ?? [];

  if (!clientLoading && !client) {
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
              {client?.name ?? "Loading..."}
            </h1>
            {client?.description && (
              <p className="text-sm text-muted-foreground">
                {client.description}
              </p>
            )}
          </div>
          <div className="flex gap-2">
            <Button onClick={() => setShowCreateMeeting(true)}>
              <Plus className="h-4 w-4" />
              New Meeting
            </Button>
            <Button onClick={() => setShowCreateProject(true)}>
              <Plus className="h-4 w-4" />
              New Project
            </Button>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-4 md:p-6">
        <div className="mb-8">
          <h2 className="mb-4 text-lg font-medium">Projects</h2>
          {projects.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 text-center">
              <p className="mb-4 text-sm text-muted-foreground">
                No projects yet
              </p>
              <Button onClick={() => setShowCreateProject(true)}>
                <Plus className="h-4 w-4" />
                Create Project
              </Button>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {projects.map((project: { id: string; name: string; description?: string | null; status?: string }) => (
                <Link key={project.id} href={`/projects/${project.id}`}>
                  <Card className="transition-shadow hover:shadow-sm">
                    <CardHeader>
                      <CardTitle>{project.name}</CardTitle>
                      {project.description && (
                        <CardDescription className="line-clamp-2">
                          {project.description}
                        </CardDescription>
                      )}
                    </CardHeader>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </div>

        <div className="mb-8">
          <h2 className="mb-4 text-lg font-medium">
            Miscellaneous Meetings
            {meetings.length > 0 && (
              <span className="ml-2 text-sm text-muted-foreground">
                ({meetings.length})
              </span>
            )}
          </h2>
          {meetings.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 text-center">
              <p className="mb-4 text-sm text-muted-foreground">
                No miscellaneous meetings yet
              </p>
              <Button onClick={() => setShowCreateMeeting(true)}>
                <Plus className="h-4 w-4" />
                Create Meeting
              </Button>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {meetings.map((meeting: {
                id: string;
                title: string;
                meeting_date?: string | null;
                tags?: string[];
              }) => (
                <Link key={meeting.id} href={`/meetings/${meeting.id}`}>
                  <Card className="transition-shadow hover:shadow-sm">
                    <CardHeader>
                      <CardTitle className="text-base">{meeting.title}</CardTitle>
                      {meeting.meeting_date && (
                        <CardDescription>
                          {new Date(meeting.meeting_date).toLocaleDateString()}
                        </CardDescription>
                      )}
                      {meeting.tags && meeting.tags.length > 0 && (
                        <CardDescription className="flex flex-wrap gap-1">
                          {meeting.tags.map((tag) => (
                            <span
                              key={tag}
                              className="inline-block rounded-full bg-secondary px-2 py-0.5 text-xs"
                            >
                              {tag}
                            </span>
                          ))}
                        </CardDescription>
                      )}
                    </CardHeader>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </div>

        <Separator className="mb-6" />

        <MembersSection
          resourceType="client"
          resourceId={clientId}
          members={members}
          pendingInvitations={pendingInvitations}
          currentUserId={user?.id}
          onRemove={(userId) => removeMember({ clientId, userId })}
          isLoading={membersLoading}
        />
      </div>

      <CreateProjectModal
        open={showCreateProject}
        onClose={() => setShowCreateProject(false)}
        clientId={clientId}
      />

      <CreateMeetingModal
        open={showCreateMeeting}
        onClose={() => setShowCreateMeeting(false)}
        clientId={clientId}
      />
    </>
  );
}
