"use client";

import { useParams, useRouter } from "next/navigation";
import { Menu, ArrowLeft, RefreshCw, Upload, Loader2 } from "lucide-react";
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
import { useAppContext } from "@/lib/app-context";
import {
  useMeeting,
  useMeetingAnalysis,
  useRegenerateAnalysis,
  useUploadTranscript,
} from "@/hooks/useMeetings";

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

export default function MeetingPage() {
  const params = useParams();
  const router = useRouter();
  const meetingId = params.meetingId as string;
  const { setSidebarOpen } = useAppContext();

  const { data: meetingData } = useMeeting(meetingId);
  const { data: analysisData, isLoading: analysisLoading } =
    useMeetingAnalysis(meetingId);
  const regenerateAnalysis = useRegenerateAnalysis();
  const uploadTranscript = useUploadTranscript();

  const meeting = meetingData?.data;
  const analysis = analysisData?.data;

  const handleRegenerate = () => {
    regenerateAnalysis.mutate(meetingId);
  };

  const handleFileUpload = async (file: File) => {
    await uploadTranscript.mutateAsync({ meetingId, file });
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
        {!meeting?.transcript ? (
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
    </>
  );
}
