from fastapi import APIRouter

from src.api.v1.health import router as health_router
from src.api.v1.workspaces import router as workspaces_router
from src.api.v1.clients import router as clients_router
from src.api.v1.projects import router as projects_router
from src.api.v1.meetings import router as meetings_router
from src.api.v1.transcripts import router as transcripts_router
from src.api.v1.meeting_analysis import router as meeting_analysis_router
from src.api.v1.auth import router as auth_router
from src.api.v1.webhooks import router as webhooks_router
from src.api.v1.knowledge import router as knowledge_router
from src.api.v1.assistant import router as assistant_router
from src.api.v1.meeting_suggestions import router as meeting_suggestions_router
from src.api.v1.invitations import router as invitations_router
from src.api.v1.members import router as members_router
from src.api.v1.workspace_jira import router as workspace_jira_router
from src.api.v1.project_jira import router as project_jira_router
from src.api.v1.action_item_jira import router as action_item_jira_router
from src.api.v1.api_keys import router as api_keys_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(workspaces_router)
api_router.include_router(clients_router)
api_router.include_router(projects_router)
api_router.include_router(meetings_router)
api_router.include_router(transcripts_router)
api_router.include_router(meeting_analysis_router)
api_router.include_router(webhooks_router)
api_router.include_router(knowledge_router)
api_router.include_router(assistant_router)
api_router.include_router(meeting_suggestions_router)
api_router.include_router(invitations_router)
api_router.include_router(members_router)
api_router.include_router(workspace_jira_router)
api_router.include_router(project_jira_router)
api_router.include_router(action_item_jira_router)
api_router.include_router(api_keys_router)
