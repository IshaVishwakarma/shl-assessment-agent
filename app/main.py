from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.models.schemas import (
    ChatRequest,
    ChatResponse
)

from app.services.orchestrator import process_chat

from scripts.ingest_chroma import ingest_data


# -----------------------------
# APP STARTUP
# -----------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):

    try:

        ingest_data()

        print(
            "Chroma ingestion complete."
        )

    except Exception as e:

        print(
            f"Ingestion skipped: {e}"
        )

    yield


# -----------------------------
# FASTAPI APP
# -----------------------------

app = FastAPI(
    title="SHL Assessment Recommender",
    lifespan=lifespan
)


# -----------------------------
# HEALTH
# -----------------------------

@app.get("/health")
async def health():

    return {
        "status": "ok"
    }


# -----------------------------
# CHAT
# -----------------------------

@app.post(
    "/chat",
    response_model=ChatResponse
)

async def chat(request: ChatRequest):

    response = process_chat(
        [
            msg.dict()
            for msg in request.messages
        ]
    )

    return response