from typing import Literal

from pydantic import BaseModel


class HealthRootData(BaseModel):
    project: str
    version: str
    status: Literal["healthy"]


class HealthCheckData(BaseModel):
    status: Literal["healthy"]
    database: Literal["connected", "disconnected"]
