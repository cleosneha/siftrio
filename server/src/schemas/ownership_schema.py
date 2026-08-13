from uuid import UUID

from pydantic import BaseModel


class OwnershipTransferRequest(BaseModel):
    user_id: UUID
