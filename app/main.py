from fastapi import FastAPI

from app.models.schemas import (
    ChatRequest,
    ChatResponse
)

from app.services.orchestrator import process_chat


app = FastAPI(
    title="SHL Assessment Recommender"
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
        [msg.dict() for msg in request.messages]
    )

    return response