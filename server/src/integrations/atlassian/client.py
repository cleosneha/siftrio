import logging

from authlib.integrations.httpx_client import AsyncOAuth2Client

API_BASE = "https://api.atlassian.com"

logger = logging.getLogger(__name__)


class JiraAPIError(Exception):
    def __init__(self, status_code: int, body: str) -> None:
        self.status_code = status_code
        self.body = body
        super().__init__(f"Jira API error {status_code}: {body[:300]}")


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
        resp = await self._client.get(self._url("/project/search"), params={"maxResults": 100})
        if resp.status_code == 200:
            return resp.json().get("values", [])
        raise JiraAPIError(resp.status_code, resp.text)

    async def create_project(
        self,
        key: str,
        name: str,
        project_type_key: str = "software",
        template_key: str = "com.pyxis.greenhopper.jira:gh-simplified-agility-scrum",
        lead_account_id: str | None = None,
    ) -> dict:
        payload: dict[str, object] = {
            "key": key,
            "name": name,
            "projectTypeKey": project_type_key,
        }
        if template_key:
            payload["projectTemplateKey"] = template_key
        if lead_account_id:
            payload["leadAccountId"] = lead_account_id

        resp = await self._client.post(self._url("/project"), json=payload)
        if resp.status_code == 201:
            return resp.json()
        raise JiraAPIError(resp.status_code, resp.text)

    async def get_issue_types(self, jira_project_id: str) -> list[dict]:
        resp = await self._client.get(
            self._url(f"/project/{jira_project_id}/hierarchy"),
        )
        if resp.status_code == 200:
            body = resp.json()
            hierarchy = body.get("hierarchy", [])
            issue_types = []
            for level in hierarchy:
                if level.get("level", 0) == -1:
                    continue
                for it in level.get("issueTypes", []):
                    issue_types.append(it)
            return issue_types
        raise JiraAPIError(resp.status_code, resp.text)

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
        resp = await self._client.get(url, params=params)
        if resp.status_code == 200:
            return resp.json()
        raise JiraAPIError(resp.status_code, resp.text)

    async def get_issue(self, issue_id_or_key: str) -> dict:
        resp = await self._client.get(self._url(f"/issue/{issue_id_or_key}"))
        if resp.status_code == 200:
            return resp.json()
        raise JiraAPIError(resp.status_code, resp.text)

    async def create_issue(self, fields: dict) -> dict:
        payload: dict[str, object] = {"fields": fields}
        resp = await self._client.post(self._url("/issue"), json=payload)
        if resp.status_code == 201:
            return resp.json()
        raise JiraAPIError(resp.status_code, resp.text)
