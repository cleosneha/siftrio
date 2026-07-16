export interface WorkspaceJira {
  id: string;
  workspace_id: string;
  provider: string;
  cloud_id: string | null;
  cloud_name: string | null;
  site_url: string | null;
  connected_by: string | null;
  connected_at: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface AtlassianSite {
  id: string;
  name: string;
  url: string;
}

export interface JiraProjectItem {
  id: string;
  key: string;
  name: string;
  projectTypeKey: string | null;
  style: string | null;
}

export interface ProjectJira {
  id: string;
  project_id: string;
  provider: string;
  jira_project_id: string;
  jira_project_key: string;
  jira_project_name: string;
  jira_project_type: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface JiraIssueType {
  id: string;
  name: string;
  description: string | null;
  subtask: boolean;
}

export interface JiraUser {
  account_id: string;
  display_name: string;
  email_address: string | null;
}

export interface ActionItemJiraPreview {
  summary: string;
  description: string;
  issue_type: string;
  priority: string;
  labels: string[];
  assignee: string | null;
}

export interface ActionItemJiraCreateRequest {
  summary: string;
  description: string;
  issue_type_id: string;
  priority: string;
  labels: string[];
  assignee_account_id: string | null;
  assignee_name: string | null;
  assignee_email: string | null;
}

export interface ActionItemJiraCreateResponse {
  issue_id: string;
  issue_key: string;
  issue_url: string;
}

export interface JiraIssueDetails {
  issue_id: string;
  issue_key: string;
  summary: string;
  description: string | null;
  status: string | null;
  status_category: string | null;
  issue_type: string | null;
  priority: string | null;
  assignee: string | null;
  assignee_email: string | null;
  reporter: string | null;
  labels: string[];
  created: string | null;
  updated: string | null;
  url: string;
}
