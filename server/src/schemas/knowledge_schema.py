from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class KnowledgeBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    meeting_id: UUID
    source_chunk_id: UUID | None = None
    title: str
    description: str | None = None
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    meeting_title: str | None = None


class RequirementCreate(BaseModel):
    project_id: str
    meeting_id: str
    source_chunk_id: str | None = None
    title: str
    description: str | None = None
    priority: str | None = None


class RequirementUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    status: str | None = None


class RequirementResponse(KnowledgeBaseResponse):
    priority: str | None = None
    approved_by: UUID | None = None
    approved_at: datetime | None = None


class ActionItemCreate(BaseModel):
    project_id: str
    meeting_id: str
    source_chunk_id: str | None = None
    title: str
    description: str | None = None
    assignee: str | None = None
    due_date: str | None = None


class ActionItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee: str | None = None
    due_date: str | None = None
    status: str | None = None


class ActionItemResponse(KnowledgeBaseResponse):
    assignee: str | None = None
    due_date: datetime | None = None


class DecisionCreate(BaseModel):
    project_id: str
    meeting_id: str
    source_chunk_id: str | None = None
    title: str
    description: str | None = None
    decision_date: str | None = None


class DecisionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    decision_date: str | None = None
    status: str | None = None


class DecisionResponse(KnowledgeBaseResponse):
    decision_date: datetime | None = None


class RiskCreate(BaseModel):
    project_id: str
    meeting_id: str
    source_chunk_id: str | None = None
    title: str
    description: str | None = None
    severity: str | None = None
    mitigation: str | None = None


class RiskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: str | None = None
    mitigation: str | None = None
    status: str | None = None


class RiskResponse(KnowledgeBaseResponse):
    severity: str | None = None
    mitigation: str | None = None


class QuestionCreate(BaseModel):
    project_id: str
    meeting_id: str
    source_chunk_id: str | None = None
    title: str
    description: str | None = None
    answer: str | None = None


class QuestionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    answer: str | None = None
    status: str | None = None


class QuestionResponse(KnowledgeBaseResponse):
    answer: str | None = None
