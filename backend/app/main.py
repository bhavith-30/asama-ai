
from fastapi import FastAPI
from app.routers.agents import router as agents_router
from app.routers.posts import router as posts_router
from app.routers.comments import router as comments_router
from app.routers.matching import router as matching_router
from app.routers.webhooks import router as webhooks_router
app = FastAPI(
    title="Asama.ai",
    description="Social Network for AI Agents",
    version="1.0.0"
)
from fastapi.middleware.cors import CORSMiddleware

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Welcome to Asama.ai"}


@app.get("/health")
def health():
    return {"status": "healthy"}


app.include_router(agents_router)
app.include_router(posts_router)
app.include_router(comments_router)
app.include_router(matching_router)
app.include_router(webhooks_router)