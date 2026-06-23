from pydantic import BaseModel


class ProjectCreate(BaseModel):
    client_id: str
    name: str
    description: str | None = None


class ProjectResponse(BaseModel):
    id: str
    client_id: str
    name: str
    description: str | None = None
    status: str = "active"
    created_at: str | None = None
    updated_at: str | None = None
