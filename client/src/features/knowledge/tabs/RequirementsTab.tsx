"use client";

import { useRequirements, useUpdateRequirement } from "@/hooks/useKnowledge";
import { KnowledgeTabBase } from "../KnowledgeTabBase";

export function RequirementsTab({ projectId }: { projectId: string }) {
  const { data, isLoading } = useRequirements(projectId);
  const updateMutation = useUpdateRequirement();

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading...</p>;

  return (
    <KnowledgeTabBase
      items={data?.data ?? []}
      label="Requirement"
      onUpdate={(id, d) => updateMutation.mutateAsync({ id, data: d })}
      config={{
        fields: [
          { key: "title", label: "Title" },
          { key: "description", label: "Description", type: "textarea" },
          {
            key: "priority", label: "Priority", type: "select",
            options: [
              { label: "Low", value: "low" },
              { label: "Medium", value: "medium" },
              { label: "High", value: "high" },
              { label: "Critical", value: "critical" },
            ],
          },
        ],
        statusOptions: [
          { label: "Pending", value: "pending" },
          { label: "Approved", value: "approved" },
          { label: "Rejected", value: "rejected" },
          { label: "Implemented", value: "implemented" },
        ],
        extraBadge: (item) => item.priority ? { label: String(item.priority), variant: "outline" } : null,
        approvalActions: true,
        emptyLabel: "No requirements yet. Generate a meeting analysis to populate.",
      }}
    />
  );
}
