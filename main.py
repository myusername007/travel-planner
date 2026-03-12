from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import router
from app.db.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create tables on startup if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Travel Planner API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)
