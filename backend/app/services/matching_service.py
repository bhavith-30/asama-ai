
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.post import Post


def find_matching_agents(
    db: Session,
    post: Post,
    limit: int = 10,
    threshold: float = 0.30
):
    if post.post_embedding is None:
        return []

    # Exclude the agent who created the post
    similarity = (
        1 - Agent.interest_embedding.cosine_distance(
            post.post_embedding
        )
    )

    matches = (
        db.query(Agent, similarity.label("similarity"))
        .filter(Agent.id != post.author_agent_id)
        .filter(Agent.interest_embedding.isnot(None))
        .filter(similarity >= threshold)
        .order_by(Agent.interest_embedding.cosine_distance(
            post.post_embedding
        ))
        .limit(limit)
        .all()
    )

    return [
        {
            "agent": agent,
            "similarity": float(score)
        }
        for agent, score in matches
    ]
