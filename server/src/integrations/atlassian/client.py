import logging

from authlib.integrations.httpx_client import AsyncOAuth2Client

API_BASE = "https://api.atlassian.com"

logger = logging.getLogger(__name__)


class JiraClient:
    def __init__(self, cloud_id: str, access_token: str) -> None:
        self.cloud_id = cloud_id
        self._client = AsyncOAuth2Client()
        self._client.token = {"access_token": access_token, "token_type": "Bearer"}

    def _url(self, path: str) -> str:
        return f"{API_BASE}/ex/jira/{self.cloud_id}/rest/api/3{path}"

    async def get_current_user(self) -> dict | None:
        try:
            resp = await self._client.get(self._url("/myself"))
            if resp.status_code == 200:
                return resp.json()
            logger.error("Failed to fetch current user: %s %s", resp.status_code, resp.text)
            return None
        except Exception as exc:
            logger.error("Failed to fetch current user: %s", exc)
            return None

    async def get_projects(self) -> list[dict]:
        try:
            resp = await self._client.get(self._url("/project/search"), params={"maxResults": 100})
            if resp.status_code == 200:
                return resp.json().get("values", [])
            logger.error("Failed to fetch Jira projects: %s %s", resp.status_code, resp.text)
            return []
        except Exception as exc:
            logger.error("Failed to fetch Jira projects: %s", exc)
            return []

    async def create_project(
        self,
        key: str,
        name: str,
        project_type_key: str = "software",
        template_key: str = "com.pyxis.greenhopper.jira:gh-simplified-agility-scrum",
        lead_account_id: str | None = None,
    ) -> dict | None:
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
            resp = await self._client.post(self._url("/project"), json=payload)
            if resp.status_code == 201:
                return resp.json()
            body = resp.text or "no body"
            logger.error(
                "Jira create project failed [%s] payload=%s body=%s",
                resp.status_code, payload, body,
            )
            return None
        except Exception as exc:
            logger.error("Failed to create Jira project: %s", exc)
            return None

    async def get_issue_types(self, project_id_or_key: str) -> list[dict]:
        try:
            resp = await self._client.get(
                self._url("/issuetype/project"),
                params={"projectIdOrKey": project_id_or_key},
            )
            if resp.status_code == 200:
                return resp.json()
            logger.error("Failed to fetch issue types: %s %s", resp.status_code, resp.text)
            return []
        except Exception as exc:
            logger.error("Failed to fetch issue types: %s", exc)
            return []

    async def search_users(
        self,
        query: str,
        project: str | None = None,
        global_search: bool = False,
    ) -> list[dict]:
        if global_search:
            url = self._url("/user/search")
        else:
            url = self._url("/user/assignable/search")
        params: dict[str, object] = {"query": query, "maxResults": 10}
        if project and not global_search:
            params["project"] = project
        try:
            resp = await self._client.get(url, params=params)
            if resp.status_code == 200:
                return resp.json()
            logger.error("Failed to search Jira users: %s %s", resp.status_code, resp.text)
            return []
        except Exception as exc:
            logger.error("Failed to search Jira users: %s", exc)
            return []

    async def create_issue(self, fields: dict) -> dict | None:
        payload: dict[str, object] = {"fields": fields}
        try:
            resp = await self._client.post(self._url("/issue"), json=payload)
            if resp.status_code == 201:
                return resp.json()
            body = resp.text or "no body"
            logger.error(
                "Jira create issue failed [%s] payload=%s body=%s",
                resp.status_code, payload, body,
            )
            return None
        except Exception as exc:
            logger.error("Failed to create Jira issue: %s", exc)
            return None
