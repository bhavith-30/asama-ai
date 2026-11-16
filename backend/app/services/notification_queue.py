
import json

from app.services.redis_service import redis_client

STREAM_NAME = "agent_notifications"


def enqueue_notification(
    post_id: str,
    target_agent_id: str,
    similarity_score: float
):
    notification = {
        "post_id": post_id,
        "target_agent_id": target_agent_id,
        "similarity_score": str(similarity_score)
    }

    message_id = redis_client.xadd(
        STREAM_NAME,
        {"data": json.dumps(notification)}
    )

    return message_id


def get_pending_notifications(count: int = 10):
    return redis_client.xrange(
        STREAM_NAME,
        count=count
    )
