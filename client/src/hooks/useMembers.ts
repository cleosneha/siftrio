"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { memberService } from "@/services/member.service";

export function useWorkspaceMembers(workspaceId: string) {
  return useQuery({
    queryKey: ["workspace-members", workspaceId],
    queryFn: () => memberService.listWorkspaceMembers(workspaceId),
    enabled: !!workspaceId,
  });
}

export function useClientMembers(clientId: string) {
  return useQuery({
    queryKey: ["client-members", clientId],
    queryFn: () => memberService.listClientMembers(clientId),
    enabled: !!clientId,
  });
}

export function useProjectMembers(projectId: string) {
  return useQuery({
    queryKey: ["project-members", projectId],
    queryFn: () => memberService.listProjectMembers(projectId),
    enabled: !!projectId,
  });
}

export function useRemoveWorkspaceMember() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ workspaceId, userId }: { workspaceId: string; userId: string }) =>
      memberService.removeWorkspaceMember(workspaceId, userId),
    onSuccess: (_res, { workspaceId }) => {
      queryClient.invalidateQueries({ queryKey: ["workspace-members", workspaceId] });
      queryClient.invalidateQueries({ queryKey: ["workspaces"] });
      toast.success("Member removed");
    },
    onError: () => toast.error("Failed to remove member"),
  });
}

export function useRemoveClientMember() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ clientId, userId }: { clientId: string; userId: string }) =>
      memberService.removeClientMember(clientId, userId),
    onSuccess: (_res, { clientId }) => {
      queryClient.invalidateQueries({ queryKey: ["client-members", clientId] });
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      toast.success("Member removed");
    },
    onError: () => toast.error("Failed to remove member"),
  });
}

export function useRemoveProjectMember() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, userId }: { projectId: string; userId: string }) =>
      memberService.removeProjectMember(projectId, userId),
    onSuccess: (_res, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ["project-members", projectId] });
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      toast.success("Member removed");
    },
    onError: () => toast.error("Failed to remove member"),
  });
}
