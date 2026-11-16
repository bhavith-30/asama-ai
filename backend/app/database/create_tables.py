
from sqlalchemy import text

from app.database.connection import engine, Base

# Import all models so SQLAlchemy registers them
from app.models import Agent, Post, Comment, RoutingLog


def create_tables():
    try:
        with engine.begin() as connection:

            # Enable PostgreSQL vector extension
            connection.execute(
                text("CREATE EXTENSION IF NOT EXISTS vector")
            )

            # Create all tables
            Base.metadata.create_all(bind=connection)

            # Create vector indexes for semantic search
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS
                ix_agents_interest_embedding
                ON agents USING hnsw
                (interest_embedding vector_cosine_ops)
            """))

            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS
                ix_posts_post_embedding
                ON posts USING hnsw
                (post_embedding vector_cosine_ops)
            """))

        print("Database connected successfully!")
        print("pgvector extension enabled!")
        print("All four tables created successfully!")
        print("Vector indexes created successfully!")

    except Exception as error:
        print("Database initialization failed:", error)
        raise


if __name__ == "__main__":
    create_tables()
