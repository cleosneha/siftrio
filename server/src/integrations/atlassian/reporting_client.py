import logging
from datetime import datetime

from authlib.integrations.httpx_client import AsyncOAuth2Client

REPORTING_API_URL = "https://api.atlassian.com/app/report-accounts/"

logger = logging.getLogger(__name__)


class ReportingAPIError(Exception):
    def __init__(self, status_code: int, body: str) -> None:
        self.status_code = status_code
        self.body = body
        super().__init__(f"Reporting API error {status_code}: {body[:300]}")


class AtlassianReportingClient:
    def __init__(self, access_token: str) -> None:
        self._client = AsyncOAuth2Client()
        self._client.token = {"access_token": access_token, "token_type": "Bearer"}

    async def report_accounts(
        self,
        accounts: list[dict[str, str]],
    ) -> dict:
        payload = {"accounts": accounts}
        resp = await self._client.post(REPORTING_API_URL, json=payload)

        if resp.status_code == 200:
            body = resp.json()
            return {
                "action_required": True,
                "accounts": body.get("accounts", []),
            }

        if resp.status_code == 204:
            return {"action_required": False, "accounts": []}

        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After", "60")
            raise ReportingAPIError(
                status_code=429,
                body=f"Rate limited. Retry after {retry_after}s",
            )

        raise ReportingAPIError(resp.status_code, resp.text)
