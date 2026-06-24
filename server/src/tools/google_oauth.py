from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token

from src.core.config import settings


def create_oauth_client() -> AsyncOAuth2Client:
    return AsyncOAuth2Client(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scope="openid email profile https://www.googleapis.com/auth/calendar.events",
        redirect_uri=f"{settings.BACKEND_URL}/api/auth/google/callback",
    )


def get_authorization_url() -> str:
    client = create_oauth_client()
    uri, _ = client.create_authorization_url(
        "https://accounts.google.com/o/oauth2/auth",
        prompt="select_account",
    )
    return uri


async def fetch_token(code: str) -> dict:
    client = create_oauth_client()
    token: OAuth2Token = await client.fetch_token(
        "https://oauth2.googleapis.com/token",
        code=code,
    )
    return {
        "access_token": token.get("access_token"),
        "refresh_token": token.get("refresh_token"),
        "expires_at": token.get("expires_at"),
        "scope": token.get("scope"),
    }


async def refresh_google_token(refresh_token: str) -> dict | None:
    client = create_oauth_client()
    try:
        token: OAuth2Token = await client.refresh_token(
            "https://oauth2.googleapis.com/token",
            refresh_token=refresh_token,
        )
        return {
            "access_token": token.get("access_token"),
            "refresh_token": token.get("refresh_token"),
            "expires_at": token.get("expires_at"),
            "scope": token.get("scope"),
        }
    except Exception:
        return None


async def get_google_profile(access_token: str) -> dict | None:
    client = create_oauth_client()
    client.token = {"access_token": access_token, "token_type": "Bearer"}
    try:
        resp = await client.get("https://www.googleapis.com/oauth2/v2/userinfo")
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        return None
    return None
