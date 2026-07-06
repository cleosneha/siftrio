import logging
from datetime import datetime, timezone
from urllib.parse import urlencode

from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token

from src.core.config import settings

logger = logging.getLogger(__name__)

AUTH_URL = "https://auth.atlassian.com/authorize"
TOKEN_URL = "https://auth.atlassian.com/oauth/token"
API_BASE = "https://api.atlassian.com"
SCOPES = (
    "read:jira-work write:jira-work manage:jira-project manage:jira-configuration "
    "read:jira-user offline_access"
)


def _create_client() -> AsyncOAuth2Client:
    return AsyncOAuth2Client(
        client_id=settings.ATLASSIAN_CLIENT_ID,
        client_secret=settings.ATLASSIAN_CLIENT_SECRET,
        scope=SCOPES,
        redirect_uri=f"{settings.BACKEND_URL}/api/jira/callback",
    )


def get_authorization_url(workspace_id: str) -> str:
    client = _create_client()
    params = {
        "audience": "api.atlassian.com",
        "prompt": "consent",
        "state": workspace_id,
    }
    uri, _ = client.create_authorization_url(AUTH_URL, **params)
    return uri


async def fetch_token(code: str) -> dict | None:
    client = _create_client()
    try:
        token: OAuth2Token = await client.fetch_token(TOKEN_URL, code=code)
        return {
            "access_token": token.get("access_token"),
            "refresh_token": token.get("refresh_token"),
            "expires_at": token.get("expires_at"),
            "scope": token.get("scope"),
        }
    except Exception as exc:
        logger.error("Failed to fetch Atlassian token: %s", exc)
        return None


async def refresh_access_token(refresh_token: str) -> dict | None:
    client = _create_client()
    try:
        token: OAuth2Token = await client.refresh_token(
            TOKEN_URL,
            refresh_token=refresh_token,
        )
        return {
            "access_token": token.get("access_token"),
            "refresh_token": token.get("refresh_token") or refresh_token,
            "expires_at": token.get("expires_at"),
            "scope": token.get("scope"),
        }
    except Exception as exc:
        logger.error("Failed to refresh Atlassian token: %s", exc)
        return None


async def get_accessible_resources(access_token: str) -> list[dict]:
    client = _create_client()
    client.token = {"access_token": access_token, "token_type": "Bearer"}
    try:
        resp = await client.get(
            f"{API_BASE}/oauth/token/accessible-resources"
        )
        if resp.status_code == 200:
            return resp.json()
        logger.error(
            "Failed to fetch accessible resources: %s %s",
            resp.status_code, resp.text,
        )
        return []
    except Exception as exc:
        logger.error("Failed to fetch accessible resources: %s", exc)
        return []


async def get_current_user(
    cloud_id: str,
    access_token: str,
) -> dict | None:
    client = _create_client()
    client.token = {"access_token": access_token, "token_type": "Bearer"}
    try:
        resp = await client.get(
            f"{API_BASE}/ex/jira/{cloud_id}/rest/api/3/myself"
        )
        if resp.status_code == 200:
            return resp.json()
        logger.error(
            "Failed to fetch current user: %s %s",
            resp.status_code, resp.text,
        )
        return None
    except Exception as exc:
        logger.error("Failed to fetch current user: %s", exc)
        return None


async def get_jira_projects(
    cloud_id: str,
    access_token: str,
) -> list[dict]:
    client = _create_client()
    client.token = {"access_token": access_token, "token_type": "Bearer"}
    url = f"{API_BASE}/ex/jira/{cloud_id}/rest/api/3/project/search"
    try:
        resp = await client.get(url, params={"maxResults": 100})
        if resp.status_code == 200:
            data = resp.json()
            return data.get("values", [])
        logger.error(
            "Failed to fetch Jira projects: %s %s",
            resp.status_code, resp.text,
        )
        return []
    except Exception as exc:
        logger.error("Failed to fetch Jira projects: %s", exc)
        return []


async def create_jira_project(
    cloud_id: str,
    access_token: str,
    key: str,
    name: str,
    project_type_key: str = "software",
    template_key: str = "com.pyxis.greenhopper.jira:gh-simplified-agility-scrum",
    lead_account_id: str | None = None,
) -> dict | None:
    client = _create_client()
    client.token = {"access_token": access_token, "token_type": "Bearer"}
    url = f"{API_BASE}/ex/jira/{cloud_id}/rest/api/3/project"
    payload: dict[str, object] = {
        "key": key,
        "name": name,
        "projectTypeKey": project_type_key,
    }
    if template_key:
        payload["projectTemplateKey"] = template_key
    if lead_account_id:
        payload["leadAccountId"] = lead_account_id

    try:
        resp = await client.post(url, json=payload)
        if resp.status_code == 201:
            return resp.json()
        try:
            body = resp.text or "no body"
        except Exception:
            body = "unreadable body"
        logger.error(
            "Jira create project failed [%s] payload=%s body=%s",
            resp.status_code, payload, body,
        )
        return None
    except Exception as exc:
        logger.error("Failed to create Jira project: %s", exc)
        return None


def is_token_expired(expires_at: float | None) -> bool:
    if expires_at is None:
        return True
    return datetime.now(timezone.utc).timestamp() >= expires_at - 60
