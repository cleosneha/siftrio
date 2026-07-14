"use client";

import { Loader2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useActionItemJiraIssue } from "@/features/jira/hooks/useJira";
import type { JiraIssueDetails } from "@/features/jira/types/jira.types";

interface JiraIssueDetailsModalProps {
  open: boolean;
  onClose: () => void;
  projectId: string;
  actionItemId: string;
}

export function JiraIssueDetailsModal({
  open,
  onClose,
  projectId,
  actionItemId,
}: JiraIssueDetailsModalProps) {
  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        if (!v) onClose();
      }}
    >
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Jira Issue Details</DialogTitle>
          <DialogDescription>
            Current status and details of the linked Jira issue.
          </DialogDescription>
        </DialogHeader>

        {open && actionItemId ? (
          <JiraIssueDetailsContent
            key={actionItemId}
            projectId={projectId}
            actionItemId={actionItemId}
          />
        ) : null}
      </DialogContent>
    </Dialog>
  );
}

function JiraIssueDetailsContent({
  projectId,
  actionItemId,
}: {
  projectId: string;
  actionItemId: string;
}) {
  const { data, isLoading, isError } = useActionItemJiraIssue(
    projectId,
    actionItemId,
  );
  const issue = data?.data ?? null;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError || !issue) {
    return (
      <div className="py-6 text-center text-sm text-muted-foreground">
        Failed to load Jira issue details.
      </div>
    );
  }

  return <JiraIssueDetailsBody issue={issue} />;
}

function JiraIssueDetailsBody({ issue }: { issue: JiraIssueDetails }) {
  const statusColor = getStatusColor(issue.status_category);

  return (
    <>
      <div className="grid gap-4">
        <DetailRow label="Issue" value={`${issue.issue_key}`} bold />
        <DetailRow label="Summary" value={issue.summary} />
        {issue.description && (
          <DetailRow label="Description" value={issue.description} />
        )}

        <div className="grid grid-cols-2 gap-4">
          <DetailRow label="Status" value={issue.status}>
            {issue.status && (
              <span
                className="ml-2 inline-block rounded-full px-2 py-0.5 text-xs font-medium"
                style={{
                  backgroundColor: statusColor.bg,
                  color: statusColor.text,
                }}
              >
                {issue.status}
              </span>
            )}
          </DetailRow>
          <DetailRow label="Issue Type" value={issue.issue_type} />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <DetailRow label="Priority" value={issue.priority} />
          <DetailRow label="Reporter" value={issue.reporter} />
        </div>

        <DetailRow label="Assignee" value={issue.assignee ?? "Unassigned"}>
          {issue.assignee_email && (
            <span className="ml-2 text-xs text-muted-foreground">
              ({issue.assignee_email})
            </span>
          )}
        </DetailRow>

        {issue.labels.length > 0 && (
          <DetailRow label="Labels">
            <div className="flex flex-wrap gap-1">
              {issue.labels.map((label) => (
                <span
                  key={label}
                  className="inline-block rounded-full bg-muted px-2 py-0.5 text-xs"
                >
                  {label}
                </span>
              ))}
            </div>
          </DetailRow>
        )}

        <div className="grid grid-cols-2 gap-4">
          <DetailRow
            label="Created"
            value={issue.created ? formatJiraDate(issue.created) : null}
          />
          <DetailRow
            label="Updated"
            value={issue.updated ? formatJiraDate(issue.updated) : null}
          />
        </div>
      </div>
    </>
  );
}

function DetailRow({
  label,
  value,
  bold,
  children,
}: {
  label: string;
  value?: string | null;
  bold?: boolean;
  children?: React.ReactNode;
}) {
  return (
    <div>
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <div className={`mt-0.5 text-sm ${bold ? "font-semibold" : ""}`}>
        {children ??
          (value || <span className="text-muted-foreground">—</span>)}
      </div>
    </div>
  );
}

function getStatusColor(category: string | null): { bg: string; text: string } {
  switch (category?.toLowerCase()) {
    case "to do":
      return { bg: "#dbeafe", text: "#1e40af" };
    case "in progress":
      return { bg: "#fef3c7", text: "#92400e" };
    case "done":
      return { bg: "#d1fae5", text: "#065f46" };
    default:
      return { bg: "#f3f4f6", text: "#374151" };
  }
}

function formatJiraDate(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return dateStr;
  }
}
