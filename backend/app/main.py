from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.gambling import GamblingEngine
from app.llm import ProviderError, run_demo_generation, run_live_generation
from app.roll_store import RollStore
from app.schemas import GenerateRequest, GenerateResponse, RollResponse


settings = get_settings()
engine = GamblingEngine()
roll_store = RollStore()


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(
    title="AI Gamblecore API",
    version="0.1.0",
    description="Server-authoritative gambling modifiers for LLM prompts.",
    lifespan=lifespan,
)

if settings.is_development:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/roll", response_model=RollResponse)
async def create_roll() -> RollResponse:
    roll_id = str(uuid4())
    _, rolls = engine.roll()
    roll_store.put(roll_id, rolls, settings.roll_ttl_seconds)
    return RollResponse(roll_id=roll_id, expires_in=settings.roll_ttl_seconds, rolls=rolls)


@app.post("/api/v1/generate", response_model=GenerateResponse)
async def generate(payload: GenerateRequest) -> GenerateResponse:
    rolls = roll_store.consume(payload.roll_id)
    if rolls is None:
        raise HTTPException(status_code=410, detail="Roll expired or was already used")

    if payload.demo:
        answer, final_prompt, translations = run_demo_generation(payload.prompt, rolls)
    else:
        if payload.provider is None or not payload.provider.api_key:
            raise HTTPException(status_code=422, detail="Provider and API key are required in live mode")
        try:
            answer, final_prompt, translations = await run_live_generation(
                payload.prompt, rolls, payload.provider
            )
        except ProviderError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    return GenerateResponse(
        answer=answer,
        final_prompt=final_prompt,
        rolls=rolls,
        translations=translations,
        demo=payload.demo,
    )

