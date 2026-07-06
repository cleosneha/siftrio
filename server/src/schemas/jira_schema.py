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
    connected_at: datetime | None = None
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
