import logging
import time
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from starlette.middleware.cors import CORSMiddleware

from app.chat.chatbot import chat_once
from app.chat.databases.sqlite_db import init_db, save_message, save_thread, update_thread_access


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chat_api")

app = FastAPI(title="LangGraph Chat API", version="1.0.0")



class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=128)
    chat_session_id: str = Field(..., min_length=1, max_length=128)
    new_query: str = Field(..., min_length=1, max_length=4000)

    @field_validator("user_id", "chat_session_id", "new_query")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("must not be empty")
        return trimmed


class ChatResponse(BaseModel):
    answer: str


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    try:
        save_thread(payload.user_id, payload.chat_session_id)
        save_message(payload.user_id, payload.chat_session_id, "user", payload.new_query)

        answer = chat_once(payload.user_id, payload.chat_session_id, payload.new_query)

        save_message(payload.user_id, payload.chat_session_id, "assistant", answer)
        update_thread_access(payload.user_id, payload.chat_session_id)

        latency_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "chat_success request_id=%s user_id=%s chat_session_id=%s latency_ms=%.2f",
            request_id,
            payload.user_id,
            payload.chat_session_id,
            latency_ms,
        )
        return ChatResponse(answer=answer)

    except ValueError as exc:
        logger.warning(
            "chat_validation_error request_id=%s user_id=%s chat_session_id=%s error=%s",
            request_id,
            payload.user_id,
            payload.chat_session_id,
            exc,
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception(
            "chat_failure request_id=%s user_id=%s chat_session_id=%s error=%s",
            request_id,
            payload.user_id,
            payload.chat_session_id,
            exc,
        )
        raise HTTPException(status_code=500, detail="Internal server error") from exc
