"use client";

import { useState, useCallback } from "react";
import { useParams, notFound } from "next/navigation";
import { Loader2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { knowledgeService } from "@/features/knowledge/services/knowledge.service";
import { useProjectJira } from "@/features/jira/hooks/useJira";
import { JiraPreviewModal } from "@/features/jira/components/JiraPreviewModal";
import { JiraIssueDetailsModal } from "@/features/jira/components/JiraIssueDetailsModal";
import { useMeeting, useMeetingAnalysis, useRegenerateAnalysis, useUploadTranscript, useTranscriptStatus, useMeetingSuggestions, useDismissSuggestion } from "@/features/meetings/hooks/useMeetings";
import { CreateMeetingModal } from "@/features/meetings/components/CreateMeetingModal";
import { MeetingDetailHeader } from "@/features/meetings/components/MeetingDetailHeader";
import { MeetingInfoBar } from "@/features/meetings/components/MeetingInfoBar";
import { GuestsCard } from "@/features/meetings/components/GuestsCard";
import { TranscriptPlaceholder } from "@/features/meetings/components/TranscriptPlaceholder";
import { AnalysisContent } from "@/features/meetings/components/AnalysisContent";
import type { ActionItem } from "@/types";

export default function MeetingPage() {
  const params = useParams();
  const meetingId = params.meetingId as string;

  const { data: meetingData, isLoading: meetingLoading } = useMeeting(meetingId);
  const { data: analysisData, isLoading: analysisLoading } = useMeetingAnalysis(meetingId);
  const { data: transcriptStatusData } = useTranscriptStatus(meetingId);
  const { data: suggestionsData } = useMeetingSuggestions(meetingId);
  const regenerateAnalysis = useRegenerateAnalysis();
  const uploadTranscript = useUploadTranscript();
  const dismissSuggestion = useDismissSuggestion();

  const [jiraItem, setJiraItem] = useState<ActionItem | null>(null);
  const [detailsItem, setDetailsItem] = useState<ActionItem | null>(null);
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
  const pendingSuggestions = suggestions.filter(
    (s: { status: string }) => s.status === "pending",
  );

  const projectId = meeting?.project_id ?? undefined;
  const { data: actionItemsRes } = useQuery({
    queryKey: ["meeting-action-items", meetingId],
    queryFn: () => knowledgeService.listActionItems({ meeting_id: meetingId }),
    enabled: !!meetingId,
  });
  const { data: jiraData } = useProjectJira(projectId);
  const hasJira = !!jiraData?.data;
  const meetingActionItems = actionItemsRes?.data ?? [];

  if (!meetingLoading && !meeting) {
    notFound();
  }

  const handleSchedule = useCallback(
    (suggestion: { title: string; suggested_date: string | null; start_time: string | null; end_time: string | null }) => {
      setScheduleTarget(suggestion);
    },
    [],
  );

  return (
    <>
      <MeetingDetailHeader
        title={meeting?.title ?? "Loading..."}
        date={meeting?.meeting_date ?? null}
        generatedAt={analysis?.created_at ?? null}
        isRegenerating={regenerateAnalysis.isPending}
        onRegenerate={() => regenerateAnalysis.mutate(meetingId)}
      />

      <div className="flex-1 overflow-y-auto p-4 md:p-6">
        {meeting && (
          <>
            <MeetingInfoBar
              meetingProvider={meeting.meeting_provider}
              transcriptStatus={transcriptStatus}
              meetingUrl={meeting.meeting_url}
              googleMeetUrl={meeting.google_meet_url}
            />
            <GuestsCard guests={meeting.guest_emails} />
          </>
        )}

        <TranscriptPlaceholder
          transcriptStatus={transcriptStatus}
          hasTranscript={!!meeting?.transcript}
          isUploading={uploadTranscript.isPending}
          onUpload={(file) => uploadTranscript.mutateAsync({ meetingId, file })}
        />

        {!meeting?.transcript &&
          transcriptStatus !== "processing" &&
          transcriptStatus !== "failed" ? null : analysisLoading ? (
          <div className="flex items-center justify-center p-12">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            <span className="ml-2 text-sm text-muted-foreground">
              Loading analysis...
            </span>
          </div>
        ) : analysis ? (
          <AnalysisContent
            analysis={analysis}
            actionItems={meetingActionItems}
            hasJira={hasJira}
            pendingSuggestions={pendingSuggestions}
            onOpenJira={setJiraItem}
            onViewIssue={setDetailsItem}
            onDismiss={(id) =>
              dismissSuggestion.mutate({ meetingId, suggestionId: id })
            }
            onSchedule={handleSchedule}
            isDismissing={dismissSuggestion.isPending}
          />
        ) : (
          <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-12 text-center">
            <h3 className="mb-2 text-lg font-medium">No analysis yet</h3>
            <p className="mb-4 text-sm text-muted-foreground">
              Click regenerate to generate analysis from the transcript
            </p>
            <button
              type="button"
              onClick={() => regenerateAnalysis.mutate(meetingId)}
              disabled={regenerateAnalysis.isPending}
              className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              {regenerateAnalysis.isPending ? "Generating..." : "Generate Analysis"}
            </button>
          </div>
        )}
      </div>

      <JiraPreviewModal
        open={!!jiraItem}
        onClose={() => setJiraItem(null)}
        projectId={projectId ?? ""}
        actionItemId={jiraItem?.id ?? ""}
      />

      <JiraIssueDetailsModal
        open={!!detailsItem}
        onClose={() => setDetailsItem(null)}
        projectId={projectId ?? ""}
        actionItemId={detailsItem?.id ?? ""}
      />

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
