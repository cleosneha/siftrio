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

export interface SuggestedMeeting {
  id: string;
  meeting_id: string;
  client_id: string;
  project_id: string | null;
  title: string;
  description: string | null;
  suggested_date: string | null;
  start_time: string | null;
  end_time: string | null;
  confidence: number;
  reason: string;
  status: "pending" | "scheduled" | "dismissed";
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
  start_time: string | null;
  end_time: string | null;
  meeting_provider: "manual" | "google_meet";
  meeting_url: string | null;
  google_calendar_event_id: string | null;
  google_meet_url: string | null;
  google_meet_code: string | null;
  fireflies_meeting_id: string | null;
  transcript_status: "pending" | "processing" | "completed" | "failed" | null;
  guest_emails: string[];
  created_at: string | null;
  updated_at: string | null;
}

export interface MeetingAnalysis {
  id: string;
  meeting_id: string;
  summary: string | null;
  goal: string | null;
  outcomes: string[];
  decisions: string[];
  action_items: string[];
  answered_questions: string[];
  unanswered_questions: string[];
  risks: string[];
  blockers: string[];
  future_meetings: string[];
  generated_at: string | null;
}

export interface KnowledgeBase {
  id: string;
  project_id: string;
  meeting_id: string;
  source_chunk_id: string | null;
  title: string;
  description: string | null;
  status: string;
  created_at: string | null;
  updated_at: string | null;
  meeting_title: string | null;
  [key: string]: unknown;
}

export interface Requirement extends KnowledgeBase {
  priority: string | null;
  approved_by: string | null;
  approved_at: string | null;
}

export interface ActionItem extends KnowledgeBase {
  assignee: string | null;
  due_date: string | null;
}

export interface Decision extends KnowledgeBase {
  decision_date: string | null;
}

export interface Risk extends KnowledgeBase {
  severity: string | null;
  mitigation: string | null;
}

export interface Question extends KnowledgeBase {
  answer: string | null;
}
