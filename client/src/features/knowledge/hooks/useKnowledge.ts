"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { knowledgeService } from "@/features/knowledge/services/knowledge.service";

function useListQuery<T>(key: (string | undefined)[], fn: () => Promise<{ data: T }>, enabled?: boolean) {
  return useQuery({
    queryKey: key,
    queryFn: fn,
    enabled,
  });
}

function useUpdateMutation<T>(
  key: string[],
  fn: (args: { id: string; data: Partial<T> }) => Promise<{ message?: string }>,
  successMsg: string,
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: fn,
    onSuccess: (res) => {
      for (const k of key) {
        queryClient.invalidateQueries({ queryKey: [k] });
      }
      toast.success(res?.message || successMsg);
    },
    onError: () => {
      toast.error("Update failed");
    },
  });
}

export function useRequirements(projectId?: string) {
  return useListQuery(
    ["requirements", projectId].filter(Boolean) as string[],
    () => knowledgeService.listRequirements({ project_id: projectId }),
    !!projectId,
  );
}

export function useUpdateRequirement() {
  return useUpdateMutation(
    ["requirements"],
    ({ id, data }) => knowledgeService.updateRequirement(id, data),
    "Requirement updated",
  );
}

export function useActionItems(projectId?: string) {
  return useListQuery(
    ["action-items", projectId].filter(Boolean) as string[],
    () => knowledgeService.listActionItems({ project_id: projectId }),
    !!projectId,
  );
}

export function useUpdateActionItem() {
  return useUpdateMutation(
    ["action-items"],
    ({ id, data }) => knowledgeService.updateActionItem(id, data),
    "Action item updated",
  );
}

export function useDecisions(projectId?: string) {
  return useListQuery(
    ["decisions", projectId].filter(Boolean) as string[],
    () => knowledgeService.listDecisions({ project_id: projectId }),
    !!projectId,
  );
}

export function useUpdateDecision() {
  return useUpdateMutation(
    ["decisions"],
    ({ id, data }) => knowledgeService.updateDecision(id, data),
    "Decision updated",
  );
}

export function useRisks(projectId?: string) {
  return useListQuery(
    ["risks", projectId].filter(Boolean) as string[],
    () => knowledgeService.listRisks({ project_id: projectId }),
    !!projectId,
  );
}

export function useUpdateRisk() {
  return useUpdateMutation(
    ["risks"],
    ({ id, data }) => knowledgeService.updateRisk(id, data),
    "Risk updated",
  );
}

export function useQuestions(projectId?: string) {
  return useListQuery(
    ["questions", projectId].filter(Boolean) as string[],
    () => knowledgeService.listQuestions({ project_id: projectId }),
    !!projectId,
  );
}

export function useUpdateQuestion() {
  return useUpdateMutation(
    ["questions"],
    ({ id, data }) => knowledgeService.updateQuestion(id, data),
    "Question updated",
  );
}
