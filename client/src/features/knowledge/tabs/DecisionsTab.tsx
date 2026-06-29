"use client";

import { useDecisions, useUpdateDecision } from "@/hooks/useKnowledge";
import { KnowledgeTabBase } from "../KnowledgeTabBase";

export function DecisionsTab({ projectId }: { projectId: string }) {
  const { data, isLoading } = useDecisions(projectId);
  const updateMutation = useUpdateDecision();

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading...</p>;

  return (
    <KnowledgeTabBase
      items={data?.data ?? []}
      label="Decision"
      onUpdate={(id, d) => updateMutation.mutateAsync({ id, data: d })}
      config={{
        fields: [
          { key: "title", label: "Title" },
          { key: "description", label: "Description", type: "textarea" },
          { key: "decision_date", label: "Decision Date", type: "date" },
        ],
        statusOptions: [
          { label: "Active", value: "active" },
          { label: "Superseded", value: "superseded" },
        ],
        emptyLabel: "No decisions yet. Generate a meeting analysis to populate.",
      }}
    />
  );
}
