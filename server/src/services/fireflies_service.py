import hashlib
import hmac
import json
import logging

import httpx

from src.core.config import settings
from src.exceptions.base import BaseAPIException
from src.repositories.meeting_repository import MeetingRepository
from src.services.transcript_service import TranscriptService
from src.models.meeting import MeetingProvider, MeetingType, TranscriptStatus

logger = logging.getLogger(__name__)

FIREFLIES_GRAPHQL_URL = "https://api.fireflies.ai/graphql"


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    secret = settings.FIREFLIES_WEBHOOK_SECRET
    if not secret:
        logger.warning("FIREFLIES_WEBHOOK_SECRET not configured")
        return False
    expected = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


async def fetch_fireflies_transcript(meeting_id: str) -> dict | None:
    api_key = settings.FIREFLIES_API_KEY
    if not api_key:
        logger.warning("FIREFLIES_API_KEY not configured")
        return None

    query = """
    query Transcript($meetingId: String!) {
      transcript(id: $meetingId) {
        id
        title
        date
        calendar_id
        meeting_link
        conference_id
        transcript_url
        duration
        sentences {
          index
          speaker_name
          text
          start_time
          end_time
        }
        summary {
          keywords
          action_items
          overview
          short_summary
        }
      }
    }
    """

    variables = {"meetingId": meeting_id}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                FIREFLIES_GRAPHQL_URL,
                json={"query": query, "variables": variables},
                headers=headers,
                timeout=30,
            )
        if resp.status_code != 200:
            logger.error("Fireflies GraphQL error: %s %s", resp.status_code, resp.text)
            return None
        result = resp.json()
        if "errors" in result:
            logger.error("Fireflies GraphQL errors: %s", result["errors"])
            return None
        transcript = result.get("data", {}).get("transcript")
        if not transcript:
            logger.warning("No transcript found for meetingId: %s", meeting_id)
            return None
        return transcript
    except Exception as e:
        logger.error("Failed to fetch Fireflies transcript: %s", e)
        return None


def _build_transcript_text(transcript: dict) -> str:
    sentences = transcript.get("sentences") or []
    lines = []
    for s in sentences:
        speaker = s.get("speaker_name", "Speaker")
        text = s.get("text", "")
        lines.append(f"{speaker}: {text}")
    return "\n".join(lines) if lines else transcript.get("title", "")


async def process_fireflies_transcript(
    db_session,
    fireflies_meeting_id: str,
) -> dict:
    repo = MeetingRepository(db_session)

    transcript = await fetch_fireflies_transcript(fireflies_meeting_id)
    if not transcript:
        raise BaseAPIException(
            message="Failed to retrieve transcript from Fireflies",
            status_code=500,
        )

    meeting = None

    calendar_id = transcript.get("calendar_id")
    if calendar_id:
        meeting = await repo.find_by_google_event_id(calendar_id)
        if meeting:
            logger.info("Matched by calendar_id: %s", calendar_id)

    if not meeting:
        meeting_link = transcript.get("meeting_link")
        if meeting_link:
            meeting = await repo.find_by_google_meet_url(meeting_link)
            if meeting:
                logger.info("Matched by meeting_link: %s", meeting_link)

    if not meeting:
        conference_id = transcript.get("conference_id")
        if conference_id:
            meeting = await repo.find_by_google_meet_code(conference_id)
            if meeting:
                logger.info("Matched by conference_id: %s", conference_id)

    if not meeting:
        logger.warning(
            "No matching meeting found for Fireflies transcript %s",
            fireflies_meeting_id,
        )
        raise BaseAPIException(
            message="No matching meeting found for Fireflies transcript",
            status_code=404,
        )

    await repo.update(
        meeting.id,
        fireflies_meeting_id=fireflies_meeting_id,
        transcript_status=TranscriptStatus.PROCESSING.value,
    )

    transcript_text = _build_transcript_text(transcript)

    transcript_service = TranscriptService(db_session)
    result = await transcript_service.process_upload(meeting.id, transcript_text)

    await repo.update(
        meeting.id,
        transcript_status=TranscriptStatus.COMPLETED.value,
    )

    return {
        "meeting_id": str(meeting.id),
        "chunk_count": result["chunk_count"],
        "title": meeting.title,
    }
