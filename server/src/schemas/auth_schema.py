from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None = None
    profile_picture: str | None = None


class TokenPayload(BaseModel):
    user_id: str
    email: str
