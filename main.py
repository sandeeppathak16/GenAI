from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import database
from multi_model_intelligent_routing_system.api import router as router1


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()

    yield

    await database.disconnect()


app = FastAPI(
    title="Gen AI",
    lifespan=lifespan,
)


app.include_router(router1)