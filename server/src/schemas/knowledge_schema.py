from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.models.base import Priority
from src.models.knowledge_base import (
    ActionItemStatus,
    DecisionStatus,
    QuestionStatus,
    RequirementStatus,
    RiskStatus,
)


class KnowledgeBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    meeting_id: UUID
    source_chunk_id: UUID | None = None
    title: str
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    meeting_title: str | None = None


class RequirementCreate(BaseModel):
    project_id: str
    meeting_id: str
    source_chunk_id: str | None = None
    title: str
    description: str | None = None
    priority: Priority | None = None


class RequirementUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: Priority | None = None
    status: RequirementStatus | None = None


class RequirementResponse(KnowledgeBaseResponse):
    status: RequirementStatus
    priority: Priority | None = None
    approved_by: UUID | None = None
    approved_at: datetime | None = None


class ActionItemCreate(BaseModel):
    project_id: str
    meeting_id: str
    source_chunk_id: str | None = None
    title: str
    description: str | None = None
    assignee_name: str | None = None
    priority: Priority | None = None
    due_date: str | None = None


class ActionItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_name: str | None = None
    priority: Priority | None = None
    due_date: str | None = None
    status: ActionItemStatus | None = None


class ActionItemResponse(KnowledgeBaseResponse):
    status: ActionItemStatus
    assignee_name: str | None = None
    priority: Priority | None = None
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
    status: DecisionStatus | None = None


class DecisionResponse(KnowledgeBaseResponse):
    status: DecisionStatus
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
    status: RiskStatus | None = None


class RiskResponse(KnowledgeBaseResponse):
    status: RiskStatus
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
    status: QuestionStatus | None = None


class QuestionResponse(KnowledgeBaseResponse):
    status: QuestionStatus
    answer: str | None = None
