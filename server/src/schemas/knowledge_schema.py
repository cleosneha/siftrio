from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeBaseResponse(BaseModel):
    id: str
    project_id: str
    meeting_id: str
    source_chunk_id: str | None = None
    title: str
    description: str | None = None
    status: str
    created_at: str | None = None
    updated_at: str | None = None

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
    approved_by: str | None = None
    approved_at: str | None = None


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
    due_date: str | None = None


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
    decision_date: str | None = None


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
