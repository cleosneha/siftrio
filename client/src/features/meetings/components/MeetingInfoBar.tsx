import { ExternalLink, Video } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { TranscriptStatusBadge } from "./TranscriptStatusBadge";

export function MeetingInfoBar({
  meetingProvider,
  transcriptStatus,
  meetingUrl,
  googleMeetUrl,
}: {
  meetingProvider: string;
  transcriptStatus: string | null | undefined;
  meetingUrl: string | null;
  googleMeetUrl: string | null;
}) {
  const providerLabel =
    meetingProvider === "google_meet" ? "Google Meet" : "Manual";
  const joinUrl = meetingUrl || googleMeetUrl;

  return (
    <div className="mb-6 flex flex-wrap items-center gap-3">
      <Badge variant="outline">
        <Video className="mr-1 h-3 w-3" />
        {providerLabel}
      </Badge>
      <TranscriptStatusBadge status={transcriptStatus} />
      {joinUrl && (
        <Button
          variant="default"
          size="sm"
          onClick={() => window.open(joinUrl, "_blank")}
        >
          <ExternalLink className="mr-1.5 h-4 w-4" />
          Join Meeting
        </Button>
      )}
    </div>
  );
}
