"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { jiraService } from "@/features/jira/services/jira.service";

export function useWorkspaceJira(workspaceId: string | undefined) {
  return useQuery({
    queryKey: ["workspace-jira", workspaceId],
    queryFn: () => jiraService.getWorkspaceJira(workspaceId!),
    enabled: !!workspaceId,
  });
}

export function useConnectWorkspaceJira() {
  return useMutation({
    mutationFn: (workspaceId: string) => jiraService.connectWorkspaceJira(workspaceId),
    onSuccess: (data) => {
      if (data.url) {
        window.open(data.url, "_blank");
      }
    },
    onError: () => {
      toast.error("Failed to initiate Jira connection");
    },
  });
}

export function useJiraSites(workspaceId: string | undefined) {
  return useQuery({
    queryKey: ["jira-sites", workspaceId],
    queryFn: () => jiraService.getJiraSites(workspaceId!),
    enabled: !!workspaceId,
  });
}

export function useProjectJira(projectId: string | undefined) {
  return useQuery({
    queryKey: ["project-jira", projectId],
    queryFn: () => jiraService.getProjectJira(projectId!),
    enabled: !!projectId,
  });
}

export function useAvailableJiraProjects(projectId: string | undefined) {
  return useQuery({
    queryKey: ["available-jira-projects", projectId],
    queryFn: () => jiraService.getAvailableJiraProjects(projectId!),
    enabled: !!projectId,
  });
}

export function useConnectProjectToJira() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      data,
    }: {
      projectId: string;
      data: {
        jira_project_id: string;
        jira_project_key: string;
        jira_project_name: string;
        jira_project_type: string | null;
      };
    }) => jiraService.connectProjectToJira(projectId, data),
    onSuccess: (res, variables) => {
      queryClient.invalidateQueries({ queryKey: ["project-jira", variables.projectId] });
      toast.success(res.message || "Jira project connected");
    },
    onError: () => {
      toast.error("Failed to connect Jira project");
    },
  });
}

export function useCreateAndConnectJiraProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      projectId,
      data,
    }: {
      projectId: string;
      data: {
        key: string;
        name: string;
        project_type_key?: string;
        template_key?: string;
      };
    }) => jiraService.createAndConnectJiraProject(projectId, data),
    onSuccess: (res, variables) => {
      queryClient.invalidateQueries({ queryKey: ["project-jira", variables.projectId] });
      toast.success(res.message || "Jira project created and connected");
    },
    onError: () => {
      toast.error("Failed to create Jira project");
    },
  });
}

export function useDisconnectProjectFromJira() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (projectId: string) => jiraService.disconnectProjectFromJira(projectId),
    onSuccess: (res, projectId) => {
      queryClient.invalidateQueries({ queryKey: ["project-jira", projectId] });
      toast.success(res.message || "Jira project disconnected");
    },
    onError: () => {
      toast.error("Failed to disconnect Jira project");
    },
  });
}
