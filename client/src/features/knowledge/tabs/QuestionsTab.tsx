"use client";

import { useQuestions, useUpdateQuestion } from "@/hooks/useKnowledge";
import { KnowledgeTabBase } from "../KnowledgeTabBase";

export function QuestionsTab({ projectId }: { projectId: string }) {
  const { data, isLoading } = useQuestions(projectId);
  const updateMutation = useUpdateQuestion();

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading...</p>;

  return (
    <KnowledgeTabBase
      items={data?.data ?? []}
      label="Question"
      onUpdate={(id, d) => updateMutation.mutateAsync({ id, data: d })}
      config={{
        fields: [
          { key: "title", label: "Question" },
          { key: "description", label: "Context", type: "textarea" },
          { key: "answer", label: "Answer", type: "textarea" },
        ],
        statusOptions: [
          { label: "Answered", value: "answered" },
          { label: "Pending", value: "pending" },
        ],
        extraBadge: (item) =>
          item.status === "answered"
            ? { label: "Answered", variant: "default" as const }
            : { label: "Pending", variant: "outline" as const },
        emptyLabel: "No questions yet. Generate a meeting analysis to populate.",
      }}
    />
  );
}
