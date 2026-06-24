import json
import logging

from fastapi import APIRouter, Request

from src.core.database import async_session_factory
from src.repositories.meeting_repository import MeetingRepository
from src.services.fireflies_service import (
    process_fireflies_transcript,
    verify_webhook_signature,
)

logger = logging.getLogger(__name__)

TRANSCRIPTION_EVENTS = {
    "transcription.completed",
    "Transcription completed",
    "meeting.transcribed",
    "meeting.summarized",
}

router = APIRouter(
    prefix="/webhooks",
    tags=["webhooks"],
)


@router.post("/fireflies")
async def fireflies_webhook(request: Request) -> dict:
    body = await request.body()

    signature = request.headers.get("x-hub-signature", "")
    logger.info("Fireflies raw signature header: %s", signature[:40] + "..." if len(signature) > 40 else signature)
    logger.info("Fireflies raw body: %s", body.decode("utf-8"))
    logger.info("Fireflies all headers: %s", dict(request.headers))

    if not verify_webhook_signature(body, signature):
        logger.warning("Invalid Fireflies webhook signature")
        return {"success": False, "message": "Invalid signature"}

    payload = json.loads(body)

    event = (
        payload.get("event")
        or payload.get("eventType")
        or ""
    )

    fireflies_meeting_id = (
        payload.get("meetingId")
        or payload.get("transcriptId")
        or payload.get("meeting_id")
        or payload.get("data", {}).get("meetingId")
        or payload.get("data", {}).get("transcriptId")
    )

    logger.info(
        "Fireflies webhook received - event: %s, fireflies_meeting_id: %s, payload: %s",
        event,
        fireflies_meeting_id,
        json.dumps(payload),
    )

    if event not in TRANSCRIPTION_EVENTS:
        logger.info("Ignoring Fireflies event: %s (accepted events: %s)", event, TRANSCRIPTION_EVENTS)
        return {"success": True, "message": "Event ignored", "event": event}

    if not fireflies_meeting_id:
        logger.warning("Fireflies webhook missing meeting identifier in payload")
        return {"success": False, "message": "Missing meeting identifier"}

    async with async_session_factory() as db:
        repo = MeetingRepository(db)

        meeting = await repo.find_by_fireflies_meeting_id(fireflies_meeting_id)
        if not meeting:
            meeting = await repo.find_by_google_event_id(fireflies_meeting_id)

        if meeting:
            logger.info("Pre-linked fireflies_meeting_id %s to meeting %s", fireflies_meeting_id, meeting.id)
            await repo.update(meeting.id, fireflies_meeting_id=fireflies_meeting_id)

        try:
            result = await process_fireflies_transcript(db, fireflies_meeting_id)
            logger.info(
                "Fireflies transcript processed for meeting %s: %s chunks",
                result["meeting_id"],
                result["chunk_count"],
            )
            return {"success": True, "message": "Transcript processed", "data": result}
        except Exception as e:
            logger.error("Fireflies webhook processing failed: %s", e)
            return {"success": False, "message": str(e)}
