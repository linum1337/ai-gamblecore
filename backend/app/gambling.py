from __future__ import annotations

import random
import secrets
from dataclasses import dataclass

from app.schemas import RollItem


@dataclass(frozen=True)
class Option:
    label: str
    value: str
    weight: int
    rarity: str


TABLES: dict[str, tuple[Option, ...]] = {
    "translation": (
        Option("Без потерь", "none", 20, "rare"),
        Option("RU → EN → RU", "en,ru", 35, "common"),
        Option("RU → ZH → EN → RU", "zh,en,ru", 24, "rare"),
        Option("RU → JA → DE → RU", "ja,de,ru", 14, "epic"),
        Option("RU → AR → ZH → ES → RU", "ar,zh,es,ru", 7, "legendary"),
    ),
    "quality": (
        Option("На отвали", "low", 24, "common"),
        Option("Нормально", "normal", 43, "common"),
        Option("Постарайся", "high", 25, "rare"),
        Option("Абсолютный разнос", "maximum", 8, "legendary"),
    ),
    "style": (
        Option("Без стиля", "neutral", 25, "common"),
        Option("Корпоративный шаман", "corporate", 20, "common"),
        Option("Средневековый летописец", "medieval", 15, "rare"),
        Option("Токсичный ревьюер", "toxic_reviewer", 15, "rare"),
        Option("Учёный из 3026 года", "future_scientist", 13, "epic"),
        Option("Гоблин-копирайтер", "goblin", 12, "epic"),
    ),
    "format": (
        Option("Обычный текст", "plain", 35, "common"),
        Option("Чек-лист", "checklist", 25, "common"),
        Option("Таблица", "table", 18, "rare"),
        Option("JSON", "json", 12, "epic"),
        Option("Диалог двух экспертов", "dialogue", 10, "epic"),
    ),
    "language": (
        Option("Русский", "ru", 48, "common"),
        Option("English", "en", 22, "common"),
        Option("中文", "zh", 10, "rare"),
        Option("Deutsch", "de", 8, "rare"),
        Option("Español", "es", 7, "epic"),
        Option("日本語", "ja", 5, "legendary"),
    ),
    "chaos": (
        Option("Без мутаций", "none", 37, "common"),
        Option("Не больше 50 слов", "max_50_words", 19, "common"),
        Option("Добавляй эмодзи", "emoji", 16, "rare"),
        Option("Только короткие предложения", "short_sentences", 13, "rare"),
        Option("Закончи неожиданным выводом", "plot_twist", 10, "epic"),
        Option("Отвечай только вопросами", "questions_only", 5, "legendary"),
    ),
}


class GamblingEngine:
    def roll(self, seed: str | None = None) -> tuple[str, list[RollItem]]:
        seed = seed or secrets.token_hex(16)
        rng = random.Random(seed)
        results: list[RollItem] = []
        for category, options in TABLES.items():
            option = rng.choices(options, weights=[item.weight for item in options], k=1)[0]
            results.append(
                RollItem(
                    category=category,
                    label=option.label,
                    value=option.value,
                    rarity=option.rarity,  # type: ignore[arg-type]
                )
            )
        return seed, results

