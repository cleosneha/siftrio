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
  connected_at: string | null;
  created_at: string | null;
  updated_at: string | null;
}
