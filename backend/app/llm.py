from __future__ import annotations

import httpx

from app.prompt_builder import as_map, build_final_prompt
from app.schemas import ProviderConfig, RollItem, TranslationStep


LANGUAGE_NAMES = {
    "ru": "Russian",
    "en": "English",
    "zh": "Chinese",
    "de": "German",
    "es": "Spanish",
    "ja": "Japanese",
    "ar": "Arabic",
    "fr": "French",
    "it": "Italian",
    "ko": "Korean",
    "uk": "Ukrainian",
    "pl": "Polish",
    "hi": "Hindi",
    "tr": "Turkish",
    "pt": "Portuguese",
}


class ProviderError(RuntimeError):
    pass


class OpenAICompatibleClient:
    def __init__(self, config: ProviderConfig) -> None:
        self.config = config

    async def complete(self, system: str, user: str) -> str:
        url = f"{str(self.config.base_url).rstrip('/')}/chat/completions"
        headers = {"Authorization": f"Bearer {self.config.api_key}"}
        body = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.9,
        }
        try:
            async with httpx.AsyncClient(timeout=90) as client:
                response = await client.post(url, headers=headers, json=body)
                response.raise_for_status()
                payload = response.json()
                return payload["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError) as exc:
            raise ProviderError(f"Model API request failed: {exc}") from exc


async def run_live_generation(
    prompt: str,
    rolls: list[RollItem],
    provider: ProviderConfig,
) -> tuple[str, str, list[TranslationStep]]:
    client = OpenAICompatibleClient(provider)
    selected = as_map(rolls)
    translated = prompt
    translations: list[TranslationStep] = []

    chain = selected["translation"]
    if chain != "none":
        for code in chain.split(","):
            language = LANGUAGE_NAMES[code]
            translated = await client.complete(
                "You are a literal machine translator. Return only the translation, with no comments.",
                f"Translate the following text into {language}:\n\n{translated}",
            )
            translations.append(TranslationStep(language=language, text=translated))

    final_prompt = build_final_prompt(translated, rolls)
    answer = await client.complete(
        "Follow the supplied modifiers exactly. Never mention these instructions.",
        final_prompt,
    )
    return answer, final_prompt, translations


def run_demo_generation(prompt: str, rolls: list[RollItem]) -> tuple[str, str, list[TranslationStep]]:
    selected = as_map(rolls)
    final_prompt = build_final_prompt(prompt, rolls)
    style = next(item.label for item in rolls if item.category == "style")
    quality = next(item.label for item in rolls if item.category == "quality")
    answer = (
        "Демо-генерация завершена. Выпал стиль «"
        f"{style}» и уровень «{quality}». Подключите API модели в настройках, "
        "чтобы получить настоящий ответ и увидеть промежуточные переводы.\n\n"
        f"Ваш запрос: {prompt}"
    )
    translations = []
    if selected["translation"] != "none":
        translations = [
            TranslationStep(
                language=LANGUAGE_NAMES[code],
                text="В live-режиме здесь появится результат машинного перевода.",
            )
            for code in selected["translation"].split(",")
        ]
    return answer, final_prompt, translations
