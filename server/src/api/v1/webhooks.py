import json
import logging

from fastapi import APIRouter, BackgroundTasks, Request
from sqlalchemy import text

from src.core.database import async_session_factory
from src.core.embeddings import embedder
from src.models.meeting import TranscriptStatus
from src.repositories.meeting_repository import MeetingRepository
from src.services.fireflies_service import (
    FirefliesService,
    verify_webhook_signature,
)
from src.services.ingestion_service import run_ingestion_pipeline

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
async def fireflies_webhook(request: Request, background_tasks: BackgroundTasks) -> dict:
    body = await request.body()

    signature = request.headers.get("x-hub-signature", "")

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

    logger.info("Fireflies webhook received — event: %s", event)

    if event not in TRANSCRIPTION_EVENTS:
        logger.info("Ignoring Fireflies event: %s (accepted events: %s)", event, TRANSCRIPTION_EVENTS)
        return {"success": True, "message": "Event ignored", "event": event}

    if not fireflies_meeting_id:
        logger.warning("Fireflies webhook missing meeting identifier in payload")
        return {"success": False, "message": "Missing meeting identifier"}

    async with async_session_factory() as db:
        repo = MeetingRepository(db)

        existing = await repo.find_by_fireflies_meeting_id(fireflies_meeting_id)
        if existing:
            if existing.transcript_status == TranscriptStatus.PROCESSING:
                logger.info("Fireflies meeting %s is already processing", fireflies_meeting_id)
                await db.commit()
                return {"status": "already_processing"}
            if existing.transcript_status == TranscriptStatus.COMPLETED:
                logger.info("Fireflies meeting %s is already completed", fireflies_meeting_id)
                await db.commit()
                return {"status": "already_completed"}

        fireflies_service = FirefliesService(db, MeetingRepository(db), embedder)
        meeting, transcript_text = await fireflies_service.match_and_prepare(fireflies_meeting_id)

        meeting_id = meeting.id

        result = await db.execute(
            text("""
                UPDATE meetings
                SET transcript_status = 'processing'
                WHERE id = :mid
                  AND (transcript_status IS NULL OR transcript_status IN ('pending', 'failed'))
                RETURNING id
            """),
            {"mid": meeting_id},
        )
        claimed = result.fetchone()
        if not claimed:
            logger.info("Fireflies meeting %s could not be claimed (status conflict)", meeting_id)
            await db.commit()
            return {"status": "already_processing"}

        if not existing:
            await repo.update(meeting_id, fireflies_meeting_id=fireflies_meeting_id)

        await db.commit()

        background_tasks.add_task(run_ingestion_pipeline, meeting_id, transcript_text)

        logger.info("Fireflies ingestion offloaded for meeting %s", meeting_id)
        return {"success": True, "status": "accepted", "meeting_id": str(meeting_id)}
