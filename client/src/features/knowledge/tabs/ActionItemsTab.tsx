"use client";

import { useActionItems, useUpdateActionItem } from "@/hooks/useKnowledge";
import { KnowledgeTabBase } from "../KnowledgeTabBase";

export function ActionItemsTab({ projectId }: { projectId: string }) {
  const { data, isLoading } = useActionItems(projectId);
  const updateMutation = useUpdateActionItem();

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading...</p>;

  return (
    <KnowledgeTabBase
      items={data?.data ?? []}
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
        extraBadge: (item) => item.assignee ? { label: item.assignee, variant: "secondary" } : null,
        emptyLabel: "No action items yet. Generate a meeting analysis to populate.",
      }}
    />
  );
}
