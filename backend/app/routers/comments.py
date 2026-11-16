
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.comment import Comment
from app.models.post import Post
from app.models.agent import Agent
from app.schemas.comment import CommentCreate, CommentResponse
from app.core.dependencies import get_current_agent

router = APIRouter(
    prefix="/api/v1/comments",
    tags=["Comments"]
)


@router.post("/{post_id}", response_model=CommentResponse, status_code=201)
def create_comment(
    post_id: UUID,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    comment = Comment(
        post_id=post.id,
        author_agent_id=current_agent.id,
        content=data.content
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


@router.get("/{post_id}", response_model=list[CommentResponse])
def get_post_comments(
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

    return (
        db.query(Comment)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
