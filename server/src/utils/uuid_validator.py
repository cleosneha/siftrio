from uuid import UUID

from fastapi import HTTPException


def parse_optional_uuid(value: str | None, name: str = "id") -> UUID | None:
    if value is None:
        return None
    try:
        return UUID(value)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid {name} format")
