"use client";

import { useState, useCallback } from "react";
import { useParams, useRouter, notFound } from "next/navigation";
import { Menu, ArrowLeft, RefreshCw, Upload, Loader2, ExternalLink, Video, Mail, Loader, Calendar, X, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  useAppContext
} from "@/lib/app-context";
import {
  useMeeting,
  useMeetingAnalysis,
  useRegenerateAnalysis,
  useUploadTranscript,
  useTranscriptStatus,
  useMeetingSuggestions,
  useDismissSuggestion,
} from "@/hooks/useMeetings";
import { CreateMeetingModal } from "@/components/meeting/CreateMeetingModal";

function AnalysisSection({
  title,
  items,
  emptyText = "No items",
}: {
  title: string;
  items: string[];
  emptyText?: string;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <CardDescription>{emptyText}</CardDescription>
        ) : (
          <ul className="space-y-2">
            {items.map((item, i) => (
              <li key={i} className="flex gap-2 text-sm">
                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}

function TranscriptStatusBadge({ status }: { status: string | null | undefined }) {
  if (!status) return null;
  const variants: Record<string, { label: string; className: string }> = {
    pending: { label: "Pending", className: "bg-yellow-100 text-yellow-800" },
    processing: { label: "Processing", className: "bg-blue-100 text-blue-800" },
    completed: { label: "Completed", className: "bg-green-100 text-green-800" },
    failed: { label: "Failed", className: "bg-red-100 text-red-800" },
  };
  const v = variants[status] || { label: status, className: "bg-gray-100 text-gray-800" };
  return (
    <Badge className={v.className} variant="outline">
      {v.label}
    </Badge>
  );
}

export default function MeetingPage() {
  const params = useParams();
  const router = useRouter();
  const meetingId = params.meetingId as string;
  const { setSidebarOpen } = useAppContext();

  const { data: meetingData, isLoading: meetingLoading } = useMeeting(meetingId);
  const { data: analysisData, isLoading: analysisLoading } =
    useMeetingAnalysis(meetingId);
  const { data: transcriptStatusData } = useTranscriptStatus(meetingId);
  const { data: suggestionsData } = useMeetingSuggestions(meetingId);
  const regenerateAnalysis = useRegenerateAnalysis();
  const uploadTranscript = useUploadTranscript();
  const dismissSuggestion = useDismissSuggestion();

  const [scheduleTarget, setScheduleTarget] = useState<{
    title: string;
    suggested_date: string | null;
    start_time: string | null;
    end_time: string | null;
  } | null>(null);

  const meeting = meetingData?.data;
  const analysis = analysisData?.data;
  const transcriptStatus = transcriptStatusData?.data?.transcript_status;
  const suggestions = suggestionsData?.data ?? [];

  if (!meetingLoading && !meeting) {
    notFound();
  }

  const pendingSuggestions = suggestions.filter(
    (s: { status: string }) => s.status === "pending",
  );

  const handleRegenerate = () => {
    regenerateAnalysis.mutate(meetingId);
  };

  const handleFileUpload = async (file: File) => {
    await uploadTranscript.mutateAsync({ meetingId, file });
  };

  const handleDismiss = useCallback(
    (suggestionId: string) => {
      dismissSuggestion.mutate({ meetingId, suggestionId });
    },
    [meetingId, dismissSuggestion],
  );

  const handleSchedule = useCallback(
    (suggestion: { title: string; suggested_date: string | null; start_time: string | null; end_time: string | null }) => {
      setScheduleTarget(suggestion);
    },
    [],
  );

  const providerLabel =
    meeting?.meeting_provider === "google_meet" ? "Google Meet" : "Manual";

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
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex flex-1 items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold">
              {meeting?.title ?? "Loading..."}
            </h1>
            {meeting?.meeting_date && (
              <p className="text-sm text-muted-foreground">
                {new Date(meeting.meeting_date).toLocaleDateString()}
              </p>
            )}
          </div>
          <div className="flex items-center gap-2">
            {analysis?.generated_at && (
              <p className="text-xs text-muted-foreground">
                Generated{" "}
                {new Date(analysis.generated_at).toLocaleDateString()}
              </p>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={handleRegenerate}
              disabled={regenerateAnalysis.isPending}
            >
              <RefreshCw
                className={`h-4 w-4 ${regenerateAnalysis.isPending ? "animate-spin" : ""}`}
              />
              {regenerateAnalysis.isPending ? "Generating..." : "Regenerate"}
            </Button>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-4 md:p-6">
        {meeting && (
          <div className="mb-6 flex flex-wrap items-center gap-3">
            <Badge variant="outline">
              <Video className="mr-1 h-3 w-3" />
              {providerLabel}
            </Badge>
            <TranscriptStatusBadge status={transcriptStatus} />
            {(meeting.meeting_url || meeting.google_meet_url) && (
              <Button
                variant="default"
                size="sm"
                onClick={() => window.open(meeting.meeting_url || meeting.google_meet_url!, "_blank")}
              >
                <ExternalLink className="mr-1.5 h-4 w-4" />
                Join Meeting
              </Button>
            )}
          </div>
        )}

        {meeting && meeting.guest_emails.length > 0 && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Mail className="h-4 w-4" />
                Guests
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {meeting.guest_emails.map((email: string) => (
                  <Badge key={email} variant="secondary">
                    {email}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {transcriptStatus === "processing" && (
          <div className="flex items-center justify-center rounded-lg border p-12 text-center mb-6">
            <Loader className="h-5 w-5 animate-spin mr-2 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">
              Fireflies is processing the transcript...
            </span>
          </div>
        )}

        {transcriptStatus === "failed" && (
          <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-red-300 p-12 text-center mb-6">
            <h3 className="mb-2 text-lg font-medium text-red-600">Transcript processing failed</h3>
            <p className="mb-4 text-sm text-muted-foreground">
              Upload a .txt transcript manually to generate analysis
            </p>
            <Button
              onClick={() => {
                const input = document.createElement("input");
                input.type = "file";
                input.accept = ".txt";
                input.onchange = async (e) => {
                  const file = (e.target as HTMLInputElement).files?.[0];
                  if (file) await handleFileUpload(file);
                };
                input.click();
              }}
              disabled={uploadTranscript.isPending}
            >
              <Upload className="h-4 w-4" />
              {uploadTranscript.isPending ? "Uploading..." : "Upload Transcript"}
            </Button>
          </div>
        )}

        {(!meeting?.transcript && transcriptStatus !== "processing" && transcriptStatus !== "failed") ? (
          <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-12 text-center">
            <h3 className="mb-2 text-lg font-medium">No transcript yet</h3>
            <p className="mb-4 text-sm text-muted-foreground">
              Upload a .txt transcript to generate analysis
            </p>
            <Button
              onClick={() => {
                const input = document.createElement("input");
                input.type = "file";
                input.accept = ".txt";
                input.onchange = async (e) => {
                  const file = (e.target as HTMLInputElement).files?.[0];
                  if (file) await handleFileUpload(file);
                };
                input.click();
              }}
              disabled={uploadTranscript.isPending}
            >
              <Upload className="h-4 w-4" />
              {uploadTranscript.isPending ? "Uploading..." : "Upload Transcript"}
            </Button>
          </div>
        ) : analysisLoading ? (
          <div className="flex items-center justify-center p-12">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            <span className="ml-2 text-sm text-muted-foreground">
              Loading analysis...
            </span>
          </div>
        ) : analysis ? (
          <div className="space-y-6">
            {pendingSuggestions.length > 0 && (
              <Card className="border-primary/30">
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-primary" />
                    AI Suggested Follow-up Meetings
                  </CardTitle>
                  <CardDescription>
                    The AI detected these follow-up meeting suggestions in the transcript
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {pendingSuggestions.map((suggestion: {
                    id: string;
                    title: string;
                    description: string | null;
                    suggested_date: string | null;
                    start_time: string | null;
                    end_time: string | null;
                    confidence: number;
                    reason: string;
                  }) => (
                    <Card key={suggestion.id}>
                      <CardContent className="pt-4">
                        <div className="flex items-start justify-between gap-4">
                          <div className="min-w-0 flex-1">
                            <h4 className="font-medium">{suggestion.title}</h4>
                            {suggestion.description && (
                              <p className="mt-1 text-sm text-muted-foreground">
                                {suggestion.description}
                              </p>
                            )}
                            <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                              {suggestion.suggested_date && (
                                <span className="inline-flex items-center gap-1">
                                  <Calendar className="h-3 w-3" />
                                  {new Date(suggestion.suggested_date).toLocaleDateString()}
                                </span>
                              )}
                              {suggestion.start_time && (
                                <span>{suggestion.start_time}</span>
                              )}
                              {suggestion.end_time && (
                                <span>– {suggestion.end_time}</span>
                              )}
                              <Badge variant="outline" className="text-[10px]">
                                {Math.round(suggestion.confidence * 100)}% confidence
                              </Badge>
                            </div>
                            <p className="mt-1.5 text-xs italic text-muted-foreground">
                              &ldquo;{suggestion.reason}&rdquo;
                            </p>
                          </div>
                        </div>
                        <div className="mt-3 flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => handleSchedule(suggestion)}
                          >
                            <Calendar className="mr-1 h-3.5 w-3.5" />
                            Schedule Meeting
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleSchedule(suggestion)}
                          >
                            Edit &amp; Schedule
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleDismiss(suggestion.id)}
                            disabled={dismissSuggestion.isPending}
                          >
                            <X className="mr-1 h-3.5 w-3.5" />
                            Dismiss
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </CardContent>
              </Card>
            )}

            {analysis.summary && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {analysis.summary}
                  </p>
                </CardContent>
              </Card>
            )}

            {analysis.goal && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Goal</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {analysis.goal}
                  </p>
                </CardContent>
              </Card>
            )}

            <div className="grid gap-6 md:grid-cols-2">
              <AnalysisSection
                title="Outcomes"
                items={analysis.outcomes}
                emptyText="No outcomes recorded"
              />
              <AnalysisSection
                title="Decisions"
                items={analysis.decisions}
                emptyText="No decisions recorded"
              />
              <AnalysisSection
                title="Action Items"
                items={analysis.action_items}
                emptyText="No action items"
              />
              <AnalysisSection
                title="Answered Questions"
                items={analysis.answered_questions}
                emptyText="No questions answered"
              />
              <AnalysisSection
                title="Unanswered Questions"
                items={analysis.unanswered_questions}
                emptyText="No unanswered questions"
              />
              <AnalysisSection
                title="Risks"
                items={analysis.risks}
                emptyText="No risks identified"
              />
              <AnalysisSection
                title="Blockers"
                items={analysis.blockers}
                emptyText="No blockers"
              />
              <AnalysisSection
                title="Future Meetings"
                items={analysis.future_meetings}
                emptyText="No future meetings mentioned"
              />
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-12 text-center">
            <h3 className="mb-2 text-lg font-medium">No analysis yet</h3>
            <p className="mb-4 text-sm text-muted-foreground">
              Click regenerate to generate analysis from the transcript
            </p>
            <Button
              onClick={handleRegenerate}
              disabled={regenerateAnalysis.isPending}
            >
              <RefreshCw
                className={`h-4 w-4 ${regenerateAnalysis.isPending ? "animate-spin" : ""}`}
              />
              {regenerateAnalysis.isPending
                ? "Generating..."
                : "Generate Analysis"}
            </Button>
          </div>
        )}
      </div>

      <CreateMeetingModal
        open={!!scheduleTarget}
        onClose={() => setScheduleTarget(null)}
        clientId={meeting?.client_id ?? ""}
        defaultProjectId={meeting?.project_id ?? undefined}
        prefill={
          scheduleTarget
            ? (() => {
                const date = scheduleTarget.suggested_date;
                const start = scheduleTarget.start_time;
                const end = scheduleTarget.end_time;
                return {
                  title: scheduleTarget.title,
                  meeting_date: date ?? undefined,
                  start_time: date && start ? `${date}T${start}` : undefined,
                  end_time: date && end ? `${date}T${end}` : undefined,
                };
              })()
            : undefined
        }
      />
    </>
  );
}
