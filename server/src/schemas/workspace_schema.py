from pydantic import BaseModel


class WorkspaceCreate(BaseModel):
    name: str
    description: str | None = None


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
