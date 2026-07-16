from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkspaceJiraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    provider: str
    cloud_id: str | None = None
    cloud_name: str | None = None
    site_url: str | None = None
    connected_by: UUID | None = None
    connected_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AtlassianSite(BaseModel):
    id: str
    name: str
    url: str


class JiraProjectItem(BaseModel):
    id: str
    key: str
    name: str
    projectTypeKey: str | None = None
    style: str | None = None


class ProjectJiraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    provider: str
    jira_project_id: str
    jira_project_key: str
    jira_project_name: str
    jira_project_type: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CreateJiraProjectRequest(BaseModel):
    key: str
    name: str
    project_type_key: str = "software"
    template_key: str = "com.pyxis.greenhopper.jira:gh-simplified-agility-scrum"


class ConnectJiraProjectRequest(BaseModel):
    jira_project_id: str
    jira_project_key: str
    jira_project_name: str
    jira_project_type: str | None = None


class JiraIssueType(BaseModel):
    id: str
    name: str
    description: str | None = None
    subtask: bool = False


class JiraUser(BaseModel):
    account_id: str
    display_name: str
    email_address: str | None = None


class ActionItemJiraPreview(BaseModel):
    summary: str
    description: str
    issue_type: str
    priority: str
    labels: list[str] = []
    assignee: str | None = None


class ActionItemJiraCreateRequest(BaseModel):
    summary: str
    description: str
    issue_type_id: str
    priority: str
    labels: list[str] = []
    assignee_account_id: str | None = None
    assignee_name: str | None = None
    assignee_email: str | None = None


class ActionItemJiraCreateResponse(BaseModel):
    issue_id: str
    issue_key: str
    issue_url: str


class JiraIssueDetailsResponse(BaseModel):
    issue_id: str
    issue_key: str
    summary: str
    description: str | None = None
    status: str | None = None
    status_category: str | None = None
    issue_type: str | None = None
    priority: str | None = None
    assignee: str | None = None
    assignee_email: str | None = None
    reporter: str | None = None
    labels: list[str] = []
    created: str | None = None
    updated: str | None = None
    url: str



