
import json
import time
import httpx
import os
import os
from pathlib import Path
from dotenv import load_dotenv
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)
from app.core.webhook_security import generate_webhook_signature

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.agent import Agent
from app.models.routing_log import RoutingLog
from app.services.redis_service import redis_client
from app.services.notification_queue import STREAM_NAME

GROUP_NAME = "notification_workers"
CONSUMER_NAME = "worker_1"


def setup_consumer_group():
    try:
        redis_client.xgroup_create(
            STREAM_NAME,
            GROUP_NAME,
            id="0",
            mkstream=True
        )
        print("Redis consumer group created")
    except Exception as error:
        if "BUSYGROUP" in str(error):
            print("Redis consumer group already exists")
        else:
            raise



def process_notification(message_id, fields):
    db: Session = SessionLocal()

    try:
        notification = json.loads(fields["data"])

        agent = (
            db.query(Agent)
            .filter(Agent.id == notification["target_agent_id"])
            .first()
        )

        if not agent:
            print("Target agent not found:", notification["target_agent_id"])
            return False

        # Prepare webhook payload
        payload = {
            "event": "new_matching_post",
            "post_id": notification["post_id"],
            "target_agent_id": notification["target_agent_id"],
            "similarity_score": float(
                notification["similarity_score"]
            )
        }

        # Convert payload to bytes for HMAC signing
        payload_bytes = json.dumps(
            payload,
            separators=(",", ":")
        ).encode("utf-8")

        webhook_secret = os.getenv("WEBHOOK_SECRET")

        if not webhook_secret:
            raise ValueError("WEBHOOK_SECRET is not configured")

        # Generate HMAC signature
        signature = generate_webhook_signature(
            payload_bytes,
            webhook_secret
        )

        # Send signed webhook
        response = httpx.post(
            agent.webhook_url,
            content=payload_bytes,
            headers={
                "Content-Type": "application/json",
                "X-Webhook-Signature": signature
            },
            timeout=10.0
        )

        response.raise_for_status()

        db.query(RoutingLog).filter(
            RoutingLog.post_id == notification["post_id"],
            RoutingLog.target_agent_id == notification["target_agent_id"]
        ).update({"status": "NOTIFIED"})

        db.commit()

        print("Notification delivered:", agent.company_name)
        return True

    except Exception as error:
        db.rollback()
        print("Notification failed:", str(error))
        return False

    finally:
        db.close()

    db: Session = SessionLocal()
    

    try:
        notification = json.loads(fields["data"])

        agent = (
            db.query(Agent)
            .filter(
                Agent.id == notification["target_agent_id"]
            )
            .first()
        )

        if not agent:
            print("Target agent not found:", notification["target_agent_id"])
            return False

        response = httpx.post(
            agent.webhook_url,
            json={
                "event": "new_matching_post",
                "post_id": notification["post_id"],
                "target_agent_id": notification["target_agent_id"],
                "similarity_score": float(
                    notification["similarity_score"]
                )
            },
            timeout=10.0
        )

        response.raise_for_status()

        db.query(RoutingLog).filter(
            RoutingLog.post_id == notification["post_id"],
            RoutingLog.target_agent_id == notification["target_agent_id"]
        ).update({"status": "NOTIFIED"})

        db.commit()

        print("Notification delivered:", agent.company_name)
        return True

    except Exception as error:
        db.rollback()
        print("Notification failed:", str(error))
        return False

    finally:
        db.close()





def run_worker():
    setup_consumer_group()
    print("Notification worker started...", flush=True)

    while True:
        try:
            # First recover messages previously read but not acknowledged
            messages = redis_client.xreadgroup(
                GROUP_NAME,
                CONSUMER_NAME,
                {STREAM_NAME: "0"},
                count=5
            )

            entries_to_process = []

            for stream, entries in messages:
                entries_to_process.extend(entries)

            # If no pending messages, read new messages
            if not entries_to_process:
                messages = redis_client.xreadgroup(
                    GROUP_NAME,
                    CONSUMER_NAME,
                    {STREAM_NAME: ">"},
                    count=5,
                    block=5000
                )

                for stream, entries in messages:
                    entries_to_process.extend(entries)

            for message_id, fields in entries_to_process:
                print("Processing:", message_id, flush=True)

                success = process_notification(message_id, fields)

                if success:
                    redis_client.xack(
                        STREAM_NAME,
                        GROUP_NAME,
                        message_id
                    )
                    print("Acknowledged:", message_id, flush=True)
                else:
                    print(
                        "Notification failed:",
                        message_id,
                        flush=True
                    )

        except Exception as error:
            print("Worker error:", repr(error), flush=True)
            time.sleep(3)




if __name__ == "__main__":
    run_worker()
