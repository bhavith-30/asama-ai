
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.post import Post
from app.models.agent import Agent
from app.schemas.post import PostCreate, PostResponse
from app.core.dependencies import get_current_agent
from app.services.embedding_service import generate_embedding

router = APIRouter(
    prefix="/api/v1/posts",
    tags=["Posts"]
)


@router.post("/", response_model=PostResponse, status_code=201)
def create_post(
    data: PostCreate,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    try:
        embedding_text = data.title + " " + data.content
        embedding = generate_embedding(embedding_text)

        post = Post(
            author_agent_id=current_agent.id,
            title=data.title,
            content=data.content,
            post_embedding=embedding
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        return post

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create post"
        )


@router.get("/", response_model=list[PostResponse])
def get_posts(
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    posts = (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .all()
    )

    return posts


@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    return post
