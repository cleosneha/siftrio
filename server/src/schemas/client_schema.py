from pydantic import BaseModel


class ClientCreate(BaseModel):
    workspace_id: str
    name: str
    description: str | None = None


class ClientResponse(BaseModel):
    id: str
    workspace_id: str
    name: str
    description: str | None = None
    project_count: int = 0
    created_at: str | None = None
    updated_at: str | None = None
