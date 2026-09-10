from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


Rarity = Literal["common", "rare", "epic", "legendary"]


class RollItem(BaseModel):
    category: str
    label: str
    value: str
    rarity: Rarity


class RollResponse(BaseModel):
    roll_id: str
    expires_in: int
    rolls: list[RollItem]


class ProviderConfig(BaseModel):
    base_url: HttpUrl = "https://api.openai.com/v1"
    model: str = Field(default="gpt-4.1-mini", min_length=1, max_length=120)
    api_key: str = Field(default="", max_length=500)


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=10_000)
    roll_id: str
    demo: bool = True
    provider: ProviderConfig | None = None

    @field_validator("prompt")
    @classmethod
    def prompt_must_contain_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Prompt cannot be blank")
        return value


class TranslationStep(BaseModel):
    language: str
    text: str


class GenerateResponse(BaseModel):
    answer: str
    final_prompt: str
    rolls: list[RollItem]
    translations: list[TranslationStep]
    demo: bool
    burned: bool = False
