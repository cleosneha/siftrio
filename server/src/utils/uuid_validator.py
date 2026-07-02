from uuid import UUID

from fastapi import HTTPException, Path


async def validate_uuid_path(uuid_str: str = Path(...)) -> UUID:
    try:
        return UUID(uuid_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")


def parse_optional_uuid(value: str | None, name: str = "id") -> UUID | None:
    if value is None:
        return None
    try:
        return UUID(value)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid {name} format")
