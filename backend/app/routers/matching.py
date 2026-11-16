
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.agent import Agent
from app.models.post import Post
from app.models.routing_log import RoutingLog
from app.core.dependencies import get_current_agent
from app.services.matching_service import find_matching_agents
from app.services.notification_queue import enqueue_notification

router = APIRouter(
    prefix="/api/v1/matching",
    tags=["Semantic Matching"]
)


@router.post("/{post_id}")
def match_agents(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    if post.author_agent_id != current_agent.id:
        raise HTTPException(
            status_code=403,
            detail="You can only match agents for your own posts"
        )

    matches = find_matching_agents(db, post)

    results = []

    try:
        for match in matches:
            agent = match["agent"]
            score = match["similarity"]

            log = RoutingLog(
                post_id=post.id,
                target_agent_id=agent.id,
                vector_score=score,
                rerank_score=score,
                status="MATCHED"
            )

            db.add(log)

            enqueue_notification(
                post_id=str(post.id),
                target_agent_id=str(agent.id),
                similarity_score=score
            )

            results.append({
                "agent_id": str(agent.id),
                "company_name": agent.company_name,
                "industry_category": agent.industry_category,
                "similarity_score": round(score, 4)
            })

        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Matching or notification queue operation failed"
        )

    return {
        "post_id": str(post.id),
        "total_matches": len(results),
        "matches": results
    }
