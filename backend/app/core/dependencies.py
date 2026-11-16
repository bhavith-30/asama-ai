
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database.connection import get_db, settings
from app.models.agent import Agent

security = HTTPBearer()


def get_current_agent(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        agent_id = UUID(payload["sub"])

    except (JWTError, ValueError, KeyError, TypeError):
        raise credentials_exception

    agent = db.query(Agent).filter(
        Agent.id == agent_id
    ).first()

    if agent is None:
        raise credentials_exception

    return agent
