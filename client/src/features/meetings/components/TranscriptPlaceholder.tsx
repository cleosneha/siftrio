"use client";

import { Upload, Loader, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

function TranscriptUploadButton({
  onUpload,
  isPending,
}: {
  onUpload: (file: File) => void;
  isPending: boolean;
}) {
  return (
    <Button
      onClick={() => {
        const input = document.createElement("input");
        input.type = "file";
        input.accept = ".txt";
        input.onchange = async (e) => {
          const file = (e.target as HTMLInputElement).files?.[0];
          if (file) onUpload(file);
        };
        input.click();
      }}
      disabled={isPending}
    >
      <Upload className="h-4 w-4" />
      {isPending ? "Uploading..." : "Upload Transcript"}
    </Button>
  );
}

export function TranscriptPlaceholder({
  transcriptStatus,
  hasTranscript,
  isUploading,
  errorMessage,
  isRetrying,
  onUpload,
  onRetry,
}: {
  transcriptStatus: string | null | undefined;
  hasTranscript: boolean;
  isUploading: boolean;
  errorMessage?: string | null;
  isRetrying?: boolean;
  onUpload: (file: File) => void;
  onRetry?: () => void;
}) {
  if (transcriptStatus === "processing") {
    return (
      <div className="flex items-center justify-center rounded-lg border p-12 text-center mb-6">
        <Loader className="h-5 w-5 animate-spin mr-2 text-muted-foreground" />
        <span className="text-sm text-muted-foreground">
          Processing transcript...
        </span>
      </div>
    );
  }

  if (transcriptStatus === "failed") {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-12 text-center mb-6" style={{ borderColor: "var(--status-error-fg)" }}>
        <h3 className="mb-2 text-lg font-medium" style={{ color: "var(--status-error-fg)" }}>
          Transcript processing failed
        </h3>
        {errorMessage && (
          <p className="mb-4 max-w-lg text-sm text-muted-foreground break-words">
            {errorMessage}
          </p>
        )}
        <p className="mb-4 text-sm text-muted-foreground">
          Upload a .txt transcript manually or retry processing
        </p>
        <div className="flex gap-3">
          {onRetry && (
            <Button variant="outline" onClick={onRetry} disabled={isRetrying}>
              <RefreshCw className={`h-4 w-4 mr-1.5 ${isRetrying ? "animate-spin" : ""}`} />
              {isRetrying ? "Retrying..." : "Retry"}
            </Button>
          )}
          <TranscriptUploadButton onUpload={onUpload} isPending={isUploading} />
        </div>
      </div>
    );
  }

  if (!hasTranscript) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-12 text-center">
        <h3 className="mb-2 text-lg font-medium">No transcript yet</h3>
        <p className="mb-4 text-sm text-muted-foreground">
          Upload a .txt transcript to generate analysis
        </p>
        <TranscriptUploadButton onUpload={onUpload} isPending={isUploading} />
      </div>
    );
  }

  return null;
}
