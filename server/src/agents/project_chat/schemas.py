from uuid import UUID

from pydantic import BaseModel, Field


class EntityCandidate(BaseModel):
    id: UUID = Field(description="UUID of the entity")
    name: str = Field(description="Human-readable name of the entity")


class ParsedQuery(BaseModel):
    original_question: str = Field(description="The user's original question verbatim")
    intent: str = Field(description="The primary intent: query, summarize, compare, or list")
    workspace_name: str | None = Field(default=None, description="Workspace name if mentioned")
    client_name: str | None = Field(default=None, description="Client name if mentioned")
    project_name: str | None = Field(default=None, description="Project name if mentioned")
    meeting_name: str | None = Field(default=None, description="Meeting name if mentioned")
    ambiguous_names: list[str] = Field(
        default_factory=list,
        description="Entity names where the type (client/project/meeting) is uncertain",
    )
    keywords: list[str] = Field(default_factory=list, description="Extracted keywords and key phrases")
    date_range: dict | None = Field(
        default=None,
        description="Date filter with start and end ISO strings, e.g. {'start': '2025-01-01', 'end': '2025-06-30'}",
    )


class ResolvedEntities(BaseModel):
    workspace_id: UUID | None = Field(default=None, description="Resolved workspace ID")
    client_id: UUID | None = Field(default=None, description="Resolved client ID")
    project_id: UUID | None = Field(default=None, description="Resolved project ID")
    meeting_id: UUID | None = Field(default=None, description="Resolved meeting ID")
    workspace_candidates: list[EntityCandidate] = Field(
        default_factory=list,
        description="Ambiguous workspace matches",
    )
    client_candidates: list[EntityCandidate] = Field(
        default_factory=list,
        description="Ambiguous client matches",
    )
    project_candidates: list[EntityCandidate] = Field(
        default_factory=list,
        description="Ambiguous project matches",
    )
    meeting_candidates: list[EntityCandidate] = Field(
        default_factory=list,
        description="Ambiguous meeting matches",
    )


class RetrievalScope(BaseModel):
    query_text: str = Field(description="Original user question for embedding and search")
    workspace_ids: list[str] = Field(default_factory=list, description="Authorized workspaces to search")
    client_ids: list[str] = Field(default_factory=list, description="Clients to filter by")
    project_ids: list[str] = Field(default_factory=list, description="Projects to filter by")
    meeting_ids: list[str] = Field(default_factory=list, description="Meetings to filter by")
    keywords: list[str] = Field(default_factory=list, description="Search keywords")
    date_range: dict | None = Field(default=None, description="Date range filter")
    ambiguous_entities: dict[str, list[EntityCandidate]] = Field(
        default_factory=dict,
        description="Ambiguous entities requiring clarification",
    )


class Citation(BaseModel):
    source_type: str = Field(description="One of: chunk, meeting, knowledge")
    source_id: str = Field(description="UUID of the source entity")
    title: str = Field(description="Human-readable title of the source")
    excerpt: str = Field(description="Relevant text excerpt serving as evidence")
    relevance_score: float | None = Field(default=None, description="Similarity or relevance score 0-1")


class RetrievedChunk(BaseModel):
    chunk_id: str = Field(description="UUID of the chunk")
    meeting_id: str = Field(description="UUID of the parent meeting")
    chunk_index: int = Field(description="Position of the chunk within the meeting")
    chunk_text: str = Field(description="The chunk text content")
    score: float = Field(description="Combined relevance score after reranking")
    vector_score: float | None = Field(default=None, description="Similarity score from vector search")
    keyword_score: float | None = Field(default=None, description="Score from keyword/full-text search")
    metadata: dict = Field(default_factory=dict, description="Chunk metadata including workspace, project, client names")


class RetrievedMeeting(BaseModel):
    meeting_id: str = Field(description="UUID of the meeting")
    title: str = Field(description="Meeting title")
    summary: str | None = Field(default=None, description="Summary from meeting analysis if available")
    meeting_date: str | None = Field(default=None, description="Date the meeting took place")
    meeting_type: str | None = Field(default=None, description="Meeting type (project, miscellaneous)")


class RetrievedKnowledge(BaseModel):
    entity_id: str = Field(description="UUID of the knowledge entity")
    entity_type: str = Field(description="Type: requirement, action_item, decision, risk, question")
    title: str = Field(description="Entity title")
    description: str | None = Field(default=None, description="Entity description or details")
    status: str = Field(description="Current status (pending, approved, completed, etc.)")
    meeting_id: str | None = Field(default=None, description="UUID of the originating meeting")
    meeting_title: str | None = Field(default=None, description="Title of the originating meeting")


class RetrievedContext(BaseModel):
    chunks: list[RetrievedChunk] = Field(default_factory=list, description="Vector search results")
    meetings: list[RetrievedMeeting] = Field(default_factory=list, description="Meeting analysis results")
    knowledge: list[RetrievedKnowledge] = Field(default_factory=list, description="Knowledge entity results")


class ToolCall(BaseModel):
    tool: str = Field(description="Name of the MCP tool to invoke")
    args: dict = Field(default_factory=dict, description="Arguments to pass to the tool")


class ToolPlan(BaseModel):
    tool_calls: list[ToolCall] = Field(default_factory=list, description="MCP tools to invoke")
    rag_needed: bool = Field(default=True, description="Whether RAG retrieval is needed")
    rag_query: str | None = Field(default=None, description="Search query for RAG if needed")
