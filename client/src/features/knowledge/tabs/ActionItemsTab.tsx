"use client";

import { useState } from "react";
import { ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  useActionItems,
  useUpdateActionItem,
} from "@/features/knowledge/hooks/useKnowledge";
import { useProjectJira } from "@/features/jira/hooks/useJira";
import { JiraPreviewModal } from "@/features/jira/components/JiraPreviewModal";
import { JiraIssueDetailsModal } from "@/features/jira/components/JiraIssueDetailsModal";
import { KnowledgeTabBase } from "../KnowledgeTabBase";
import type { ActionItem } from "@/types";

export function ActionItemsTab({ projectId }: { projectId: string }) {
  const { data, isLoading } = useActionItems(projectId);
  const updateMutation = useUpdateActionItem();
  const { data: jiraData } = useProjectJira(projectId);
  const [jiraItem, setJiraItem] = useState<ActionItem | null>(null);
  const [detailsItem, setDetailsItem] = useState<ActionItem | null>(null);

  const jiraMapping = jiraData?.data;
  const hasJira = !!jiraMapping;

  const items: ActionItem[] = data?.data ?? [];

  if (isLoading)
    return <p className="text-sm text-muted-foreground">Loading...</p>;

  return (
    <>
      <KnowledgeTabBase
        items={items}
        label="Action Item"
        onUpdate={(id, d) => updateMutation.mutateAsync({ id, data: d })}
        config={{
          fields: [
            { key: "title", label: "Title" },
            { key: "description", label: "Description", type: "textarea" },
            { key: "assignee", label: "Assignee" },
            { key: "due_date", label: "Due Date", type: "date" },
          ],
          statusOptions: [
            { label: "Pending", value: "pending" },
            { label: "In Progress", value: "in_progress" },
            { label: "Completed", value: "completed" },
            { label: "Cancelled", value: "cancelled" },
          ],
          extraBadge: (item) => {
            const ai = item as ActionItem;
            if (ai.sync_status === "synced")
              return { label: "Jira Synced", variant: "secondary" };
            if (ai.sync_status === "failed")
              return { label: "Jira Failed", variant: "destructive" };
            if (ai.jira_issue_id)
              return { label: "Jira Linked", variant: "secondary" };
            if (ai.assignee)
              return { label: String(ai.assignee), variant: "secondary" };
            return null;
          },
          emptyLabel:
            "No action items yet. Generate a meeting analysis to populate.",
        }}
        renderActions={(item) => {
          const ai = item as ActionItem;
          if (ai.jira_issue_url && ai.sync_status === "synced") {
            return (
              <Button
                variant="ghost"
                size="xs"
                onClick={() => setDetailsItem(ai)}
              >
                <ExternalLink className="h-3 w-3" />
                View Issue
              </Button>
            );
          }
          if (ai.jira_issue_id && ai.sync_status === "failed") {
            return (
              <Button variant="ghost" size="xs" onClick={() => setJiraItem(ai)}>
                <ExternalLink className="h-3 w-3" />
                Retry Jira
              </Button>
            );
          }
          return (
            <Button
              variant="ghost"
              size="xs"
              onClick={() => setJiraItem(ai)}
              disabled={!hasJira}
              title={
                !hasJira ? "Connect a Jira project first" : "Create Jira issue"
              }
            >
              <ExternalLink className="h-3 w-3" />
              {!hasJira ? "Jira Unavailable" : "Create Jira Issue"}
            </Button>
          );
        }}
      />

      <JiraPreviewModal
        open={!!jiraItem}
        onClose={() => setJiraItem(null)}
        projectId={projectId}
        actionItemId={jiraItem?.id ?? ""}
      />

      <JiraIssueDetailsModal
        open={!!detailsItem}
        onClose={() => setDetailsItem(null)}
        projectId={projectId}
        actionItemId={detailsItem?.id ?? ""}
      />
    </>
  );
}
