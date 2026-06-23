"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { projectService } from "@/services/project.service";

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      client_id: string;
      name: string;
      description?: string | null;
    }) => projectService.create(data),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      queryClient.invalidateQueries({ queryKey: ["workspaces"] });
      toast.success(res.message || "Project created");
    },
    onError: () => {
      toast.error("Failed to create project");
    },
  });
}

export function useProjects(clientId?: string) {
  return useQuery({
    queryKey: ["projects", clientId],
    queryFn: () => projectService.list(clientId),
    enabled: !!clientId,
  });
}

export function useProject(id: string) {
  return useQuery({
    queryKey: ["project", id],
    queryFn: () => projectService.getById(id),
    enabled: !!id,
  });
}
