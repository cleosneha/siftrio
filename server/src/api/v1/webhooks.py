import json
import logging

from fastapi import APIRouter, Request

from src.core.database import async_session_factory
from src.services.fireflies_service import (
    process_fireflies_transcript,
    verify_webhook_signature,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/webhooks",
    tags=["webhooks"],
)


@router.post("/fireflies")
async def fireflies_webhook(request: Request) -> dict:
    body = await request.body()

    signature = request.headers.get("x-hub-signature", "")
    if not verify_webhook_signature(body, signature):
        logger.warning("Invalid Fireflies webhook signature")
        return {"success": False, "message": "Invalid signature"}

    payload = json.loads(body)

    event = payload.get("event", "")
    if event != "transcription.completed":
        logger.info("Ignoring Fireflies event: %s", event)
        return {"success": True, "message": "Event ignored"}

    data = payload.get("data", {})
    fireflies_meeting_id = data.get("meetingId") or data.get("transcriptId")

    if not fireflies_meeting_id:
        logger.warning("Fireflies webhook missing meetingId/transcriptId")
        return {"success": False, "message": "Missing meeting identifier"}

    async with async_session_factory() as db:
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
