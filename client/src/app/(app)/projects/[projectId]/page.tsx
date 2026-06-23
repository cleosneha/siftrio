"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { Menu, ArrowLeft, Plus, Upload } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useProject } from "@/hooks/useProjects";
import { useMeetingsByProject, useUploadTranscript } from "@/hooks/useMeetings";
import { useAppContext } from "@/lib/app-context";
import { CreateMeetingModal } from "@/components/meeting/CreateMeetingModal";

export default function ProjectPage() {
  const params = useParams();
  const projectId = params.projectId as string;
  const { setSidebarOpen } = useAppContext();
  const [showCreateMeeting, setShowCreateMeeting] = useState(false);
  const [uploadingId, setUploadingId] = useState<string | null>(null);

  const { data: projectData } = useProject(projectId);
  const { data: meetingsData } = useMeetingsByProject(projectId);
  const uploadTranscript = useUploadTranscript();

  const project = projectData?.data;
  const meetings = meetingsData?.data ?? [];

  const statusVariant: Record<
    string,
    "default" | "secondary" | "outline" | "destructive" | "ghost" | "link"
  > = {
    active: "default",
    completed: "secondary",
    archived: "outline",
  };

  const handleFileUpload = async (meetingId: string, file: File) => {
    setUploadingId(meetingId);
    try {
      await uploadTranscript.mutateAsync({ meetingId, file });
    } finally {
      setUploadingId(null);
    }
  };

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
            {project?.status && (
              <Badge variant={statusVariant[project.status] ?? "outline"}>
                {project.status}
              </Badge>
            )}
            <Button onClick={() => setShowCreateMeeting(true)}>
              <Plus className="h-4 w-4" />
              New Meeting
            </Button>
          </div>
        </div>
      </header>

      <div className="flex-1 p-4 md:p-6">
        <div className="mb-6">
          <h2 className="mb-4 text-lg font-medium">
            Meetings
            {meetings.length > 0 && (
              <span className="ml-2 text-sm text-muted-foreground">
                ({meetings.length})
              </span>
            )}
          </h2>
          {meetings.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-12 text-center">
              <p className="mb-4 text-sm text-muted-foreground">
                No meetings yet
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
                transcript?: string | null;
              }) => (
                <Card key={meeting.id} className="transition-shadow hover:shadow-sm">
                  <CardHeader>
                    <CardTitle className="text-base">
                      {meeting.title}
                    </CardTitle>
                    {meeting.meeting_date && (
                      <CardDescription>
                        {new Date(meeting.meeting_date).toLocaleDateString()}
                      </CardDescription>
                    )}
                  </CardHeader>
                  <CardContent>
                    {meeting.transcript ? (
                      <p className="text-xs text-muted-foreground">
                        Transcript uploaded
                      </p>
                    ) : (
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          disabled={uploadingId === meeting.id}
                          onClick={() => {
                            const input = document.createElement("input");
                            input.type = "file";
                            input.accept = ".txt";
                            input.onchange = async (e) => {
                              const file = (e.target as HTMLInputElement)
                                .files?.[0];
                              if (file) {
                                await handleFileUpload(meeting.id, file);
                              }
                            };
                            input.click();
                          }}
                        >
                          <Upload className="h-3.5 w-3.5" />
                          {uploadingId === meeting.id
                            ? "Uploading..."
                            : "Upload Transcript"}
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Knowledge Base</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Knowledge base is empty. Documents and insights will appear
                here.
              </CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Project Memory Chat</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Chat with the project memory. Conversations will be available
                here.
              </CardDescription>
            </CardContent>
          </Card>
        </div>
      </div>

      <CreateMeetingModal
        open={showCreateMeeting}
        onClose={() => setShowCreateMeeting(false)}
        clientId={project?.client_id ?? ""}
        defaultProjectId={projectId}
      />
    </>
  );
}
