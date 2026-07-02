import hashlib
import hmac
import json
import logging
import re

import httpx

from src.core.config import settings
from src.core.embeddings import embedder
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

    raw_sig = signature
    if signature.startswith("sha256="):
        raw_sig = signature[7:]

    expected = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    logger.info(
        "Signature verification - received prefix: %s, received length: %s, expected length: %s, match: %s",
        signature[:20] + ("..." if len(signature) > 20 else ""),
        len(signature),
        len(expected),
        hmac.compare_digest(expected, raw_sig),
    )

    return hmac.compare_digest(expected, raw_sig)


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


async def _find_meeting(repo: MeetingRepository, transcript: dict, fireflies_meeting_id: str):
    """Try to match a transcript to a meeting using multiple strategies."""
    match_log = {"fireflies_meeting_id": fireflies_meeting_id}

    calendar_id = transcript.get("calendar_id")
    if calendar_id:
        meeting = await repo.find_by_google_event_id(calendar_id)
        if meeting:
            logger.info("Matched meeting %s by calendar_id: %s", meeting.id, calendar_id)
            return meeting
        match_log["calendar_id"] = calendar_id

    meeting_link = transcript.get("meeting_link")
    if meeting_link:
        normalized = meeting_link.rstrip("/")
        meeting = await repo.find_by_google_meet_url(normalized)
        if meeting:
            logger.info("Matched meeting %s by meeting_link: %s", meeting.id, normalized)
            return meeting
        meet_code = _extract_meet_code(meeting_link)
        if meet_code:
            meeting = await repo.find_by_google_meet_code(meet_code)
            if meeting:
                logger.info("Matched meeting %s by meet_code extracted from link: %s", meeting.id, meet_code)
                return meeting
        match_log["meeting_link"] = meeting_link

    meeting = await repo.find_by_fireflies_meeting_id(fireflies_meeting_id)
    if meeting:
        logger.info("Matched meeting %s by fireflies_meeting_id: %s", meeting.id, fireflies_meeting_id)
        return meeting
    match_log["stored_fireflies_id"] = None

    logger.warning("Meeting matching failed. Match context: %s", json.dumps(match_log))
    return None


def _extract_meet_code(url: str) -> str | None:
    """Extract the Google Meet code from a meet.google.com URL."""
    match = re.search(r"meet\.google\.com/([a-z0-9-]+)", url, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


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

    meeting = await _find_meeting(repo, transcript, fireflies_meeting_id)

    if not meeting:
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

    transcript_service = TranscriptService(db_session, embeddings=embedder)
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
