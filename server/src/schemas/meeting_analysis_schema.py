from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MeetingAnalysisCreate(BaseModel):
    summary: str | None = None
    goal: str | None = None
    outcomes: list = []
    decisions: list = []
    action_items: list = []
    answered_questions: list = []
    unanswered_questions: list = []
    risks: list = []
    blockers: list = []
    future_meetings: list = []


class MeetingAnalysisResponse(BaseModel):
    id: UUID
    meeting_id: UUID
    summary: str | None = None
    goal: str | None = None
    outcomes: list = []
    decisions: list = []
    action_items: list = []
    answered_questions: list = []
    unanswered_questions: list = []
    risks: list = []
    blockers: list = []
    future_meetings: list = []
    generated_at: datetime | None = None

class RequirementItem(BaseModel):
    title: str = Field(description="Requirement title")
    description: str | None = Field(default=None, description="Detailed description")
    priority: str | None = Field(default=None, description="Priority level (low/medium/high/critical)")


class ActionItemItem(BaseModel):
    title: str = Field(description="Action item description")
    description: str | None = Field(default=None, description="Additional details")
    assignee: str | None = Field(default=None, description="Person responsible")
    due_date: str | None = Field(default=None, description="Due date if mentioned")


class DecisionItem(BaseModel):
    title: str = Field(description="Decision made")
    description: str | None = Field(default=None, description="Additional context")
    decision_date: str | None = Field(default=None, description="Date of decision if mentioned")


class RiskItem(BaseModel):
    title: str = Field(description="Risk description")
    description: str | None = Field(default=None, description="Additional details")
    severity: str | None = Field(default=None, description="Severity (low/medium/high/critical)")
    mitigation: str | None = Field(default=None, description="Mitigation strategy")


class QuestionItem(BaseModel):
    title: str = Field(description="Question text")
    description: str | None = Field(default=None, description="Additional context")
    answer: str | None = Field(default=None, description="Answer if provided")


class MeetingAnalysisOutput(BaseModel):
    summary: str = Field(description="Brief summary of the meeting")
    goal: str = Field(description="Main goal or purpose of the meeting")
    outcomes: list[str] = Field(default_factory=list, description="Key outcomes achieved")
    blockers: list[str] = Field(default_factory=list, description="Blockers or impediments")
    future_meetings: list[str] = Field(default_factory=list, description="Future meetings mentioned")
    requirements: list[RequirementItem] = Field(default_factory=list, description="Requirements gathered")
    structured_action_items: list[ActionItemItem] = Field(default_factory=list, description="Structured action items")
    structured_decisions: list[DecisionItem] = Field(default_factory=list, description="Structured decisions")
    structured_risks: list[RiskItem] = Field(default_factory=list, description="Structured risks")
    structured_questions: list[QuestionItem] = Field(default_factory=list, description="Structured questions")