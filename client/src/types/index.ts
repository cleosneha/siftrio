export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface Workspace {
  id: string;
  name: string;
  description: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface Client {
  id: string;
  workspace_id: string;
  name: string;
  description: string | null;
  project_count: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface Project {
  id: string;
  client_id: string;
  name: string;
  description: string | null;
  status: string;
  created_at: string | null;
  updated_at: string | null;
}

export interface Meeting {
  id: string;
  client_id: string;
  project_id: string | null;
  title: string;
  meeting_type: "project" | "miscellaneous";
  tags: string[];
  transcript: string | null;
  meeting_date: string | null;
  created_at: string | null;
  updated_at: string | null;
}
