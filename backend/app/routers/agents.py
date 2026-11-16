
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.connection import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentRegister, AgentResponse, AgentLogin
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.services.embedding_service import generate_embedding
from app.core.dependencies import get_current_agent


router = APIRouter(
    prefix="/api/v1/agents",
    tags=["Agents"]
)


# 1. Register a new agent
@router.post("/register", response_model=AgentResponse)
def register_agent(
    data: AgentRegister,
    db: Session = Depends(get_db)
):
    existing_agent = db.query(Agent).filter(
        Agent.email == data.email
    ).first()

    if existing_agent:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    try:
        embedding_text = (
            data.company_name + " " +
            data.industry_category + " " +
            data.interest_manifesto
        )

        embedding = generate_embedding(embedding_text)

        agent = Agent(
            company_name=data.company_name,
            email=str(data.email),
            hashed_password=hash_password(data.password),
            industry_category=data.industry_category,
            webhook_url=str(data.webhook_url),
            interest_manifesto=data.interest_manifesto,
            interest_embedding=embedding,
            trust_score=1.0
        )

        db.add(agent)
        db.commit()
        db.refresh(agent)

        return agent

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Agent registration conflict"
        )

    except Exception:
        db.rollback()
        raise


# 2. Agent login
@router.post("/login")
def login_agent(
    data: AgentLogin,
    db: Session = Depends(get_db)
):
    agent = db.query(Agent).filter(
        Agent.email == data.email
    ).first()

    if not agent or not agent.hashed_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        data.password,
        agent.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(str(agent.id))

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "agent_id": str(agent.id),
        "company_name": agent.company_name
    }


# 3. Get all agents
@router.get("/", response_model=list[AgentResponse])
def get_agents(
    db: Session = Depends(get_db)
):
    return db.query(Agent).all()


# 4. Get currently authenticated agent
@router.get("/me", response_model=AgentResponse)
def get_my_profile(
    current_agent: Agent = Depends(get_current_agent)
):
    return current_agent


# 5. Get a specific agent by UUID
@router.get("/by-id/{agent_id}", response_model=AgentResponse)
def get_agent(
    agent_id: UUID,
    db: Session = Depends(get_db)
):
    agent = db.query(Agent).filter(
        Agent.id == agent_id
    ).first()

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    return agent
