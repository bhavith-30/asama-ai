
import hmac
import os
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

from fastapi import APIRouter, Request, HTTPException
from app.core.webhook_security import verify_webhook_signature

router = APIRouter(
    prefix="/api/v1/webhooks",
    tags=["Webhooks"]
)


@router.post("/test")
async def receive_test_webhook(request: Request):

    # Read the exact raw request body
    payload = await request.body()

    # Get signature from request headers
    received_signature = request.headers.get(
        "X-Webhook-Signature"
    )

    if not received_signature:
        raise HTTPException(
            status_code=401,
            detail="Missing webhook signature"
        )

    secret = os.getenv("WEBHOOK_SECRET")

    if not secret:
        raise HTTPException(
            status_code=500,
            detail="Webhook secret is not configured"
        )

    # Verify HMAC signature
    is_valid = verify_webhook_signature(
        payload,
        secret,
        received_signature
    )

    if not is_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature"
        )

    # Parse JSON only after signature verification
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload"
        )

    print("Webhook signature verified successfully!")
    print("Payload:", data)

    return {
        "success": True,
        "message": "Webhook signature verified successfully",
        "received_data": data
    }
