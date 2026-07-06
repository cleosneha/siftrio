"use client";

import { useRisks, useUpdateRisk } from "@/features/knowledge/hooks/useKnowledge";
import { KnowledgeTabBase } from "../KnowledgeTabBase";

export function RisksTab({ projectId }: { projectId: string }) {
  const { data, isLoading } = useRisks(projectId);
  const updateMutation = useUpdateRisk();

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading...</p>;

  return (
    <KnowledgeTabBase
      items={data?.data ?? []}
      label="Risk"
      onUpdate={(id, d) => updateMutation.mutateAsync({ id, data: d })}
      config={{
        fields: [
          { key: "title", label: "Title" },
          { key: "description", label: "Description", type: "textarea" },
          {
            key: "severity", label: "Severity", type: "select",
            options: [
              { label: "Low", value: "low" },
              { label: "Medium", value: "medium" },
              { label: "High", value: "high" },
              { label: "Critical", value: "critical" },
            ],
          },
          { key: "mitigation", label: "Mitigation", type: "textarea" },
        ],
        statusOptions: [
          { label: "Open", value: "open" },
          { label: "Mitigated", value: "mitigated" },
          { label: "Closed", value: "closed" },
        ],
        extraBadge: (item) => item.severity ? { label: String(item.severity), variant: "outline" } : null,
        emptyLabel: "No risks yet. Generate a meeting analysis to populate.",
      }}
    />
  );
}
