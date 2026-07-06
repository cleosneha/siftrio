"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { workspaceService } from "@/features/workspaces/services/workspace.service";

const QUERY_KEY = ["workspaces"];

export function useCreateWorkspace() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { name: string; description?: string | null }) =>
      workspaceService.create(data),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success(res.message || "Workspace created");
    },
    onError: () => {
      toast.error("Failed to create workspace");
    },
  });
}

export function useWorkspaces() {
  return useQuery({
    queryKey: QUERY_KEY,
    queryFn: () => workspaceService.list(),
  });
}

export function useWorkspace(id: string) {
  return useQuery({
    queryKey: ["workspace", id],
    queryFn: () => workspaceService.getById(id),
    enabled: !!id,
  });
}
