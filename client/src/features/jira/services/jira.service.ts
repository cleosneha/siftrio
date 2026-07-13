import { api } from "@/lib/api";
import type { ApiResponse } from "@/types";
import type {
  ActionItemJiraCreateRequest,
  ActionItemJiraCreateResponse,
  ActionItemJiraPreview,
  AtlassianSite,
  JiraIssueType,
  JiraProjectItem,
  JiraUser,
  ProjectJira,
  WorkspaceJira,
} from "@/features/jira/types/jira.types";

export const jiraService = {
  async getWorkspaceJira(workspaceId: string) {
    const res = await api.get<ApiResponse<WorkspaceJira>>(`/workspaces/${workspaceId}/jira`);
    return res.data;
  },

  async connectWorkspaceJira(workspaceId: string) {
    const res = await api.post<{ url: string }>(`/workspaces/${workspaceId}/jira/connect`);
    return res.data;
  },

  async getJiraSites(workspaceId: string) {
    const res = await api.get<ApiResponse<AtlassianSite[]>>(`/workspaces/${workspaceId}/jira/sites`);
    return res.data;
  },

  async getProjectJira(projectId: string) {
    const res = await api.get<ApiResponse<ProjectJira>>(`/projects/${projectId}/jira`);
    return res.data;
  },

  async getAvailableJiraProjects(projectId: string) {
    const res = await api.get<ApiResponse<JiraProjectItem[]>>(`/projects/${projectId}/jira/projects`);
    return res.data;
  },

  async connectProjectToJira(projectId: string, data: {
    jira_project_id: string;
    jira_project_key: string;
    jira_project_name: string;
    jira_project_type: string | null;
  }) {
    const res = await api.post<ApiResponse<ProjectJira>>(`/projects/${projectId}/jira/connect`, data);
    return res.data;
  },

  async createAndConnectJiraProject(projectId: string, data: {
    key: string;
    name: string;
    project_type_key?: string;
    template_key?: string;
  }) {
    const res = await api.post<ApiResponse<ProjectJira>>(`/projects/${projectId}/jira/create`, data);
    return res.data;
  },

  async disconnectProjectFromJira(projectId: string) {
    const res = await api.delete<ApiResponse<null>>(`/projects/${projectId}/jira`);
    return res.data;
  },

  async getActionItemJiraPreview(projectId: string, actionItemId: string) {
    const res = await api.get<ApiResponse<ActionItemJiraPreview>>(
      `/projects/${projectId}/action-items/${actionItemId}/jira/preview`,
    );
    return res.data;
  },

  async getActionItemJiraIssueTypes(projectId: string, actionItemId: string) {
    const res = await api.get<ApiResponse<JiraIssueType[]>>(
      `/projects/${projectId}/action-items/${actionItemId}/jira/issue-types`,
    );
    return res.data;
  },

  async searchActionItemJiraUsers(projectId: string, actionItemId: string, query: string) {
    const res = await api.get<ApiResponse<JiraUser[]>>(
      `/projects/${projectId}/action-items/${actionItemId}/jira/users`,
      { params: { query } },
    );
    return res.data;
  },

  async createActionItemJiraIssue(projectId: string, actionItemId: string, data: ActionItemJiraCreateRequest) {
    const res = await api.post<ApiResponse<ActionItemJiraCreateResponse>>(
      `/projects/${projectId}/action-items/${actionItemId}/jira/issues`,
      data,
    );
    return res.data;
  },
};
