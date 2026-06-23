from fastapi import APIRouter

from src.api.v1.health import router as health_router
from src.api.v1.workspaces import router as workspaces_router
from src.api.v1.clients import router as clients_router
from src.api.v1.projects import router as projects_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(workspaces_router)
api_router.include_router(clients_router)
api_router.include_router(projects_router)
