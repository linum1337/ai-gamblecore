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
        Option("Без потерь", "none", 16, "rare"),
        Option("RU → EN → RU", "en,ru", 24, "common"),
        Option("RU → ZH → EN → RU", "zh,en,ru", 16, "rare"),
        Option("RU → FR → IT → RU", "fr,it,ru", 11, "rare"),
        Option("RU → KO → EN → RU", "ko,en,ru", 10, "epic"),
        Option("RU → JA → DE → RU", "ja,de,ru", 9, "epic"),
        Option("RU → UK → PL → DE → RU", "uk,pl,de,ru", 7, "epic"),
        Option("RU → AR → ZH → ES → RU", "ar,zh,es,ru", 4, "legendary"),
        Option("RU → HI → TR → PT → RU", "hi,tr,pt,ru", 3, "legendary"),
    ),
    "quality": (
        Option("Катастрофа", "catastrophic", 5, "epic"),
        Option("На отвали", "low", 17, "common"),
        Option("За 5 минут", "rushed", 18, "common"),
        Option("Нормально", "normal", 29, "common"),
        Option("Постарайся", "high", 19, "rare"),
        Option("Абсолютный разнос", "maximum", 8, "legendary"),
        Option("Одержимый перфекционист", "obsessive", 4, "epic"),
    ),
    "style": (
        Option("Без стиля", "neutral", 18, "common"),
        Option("Корпоративный шаман", "corporate", 12, "common"),
        Option("Средневековый летописец", "medieval", 9, "rare"),
        Option("Токсичный ревьюер", "toxic_reviewer", 9, "rare"),
        Option("Учёный из 3026 года", "future_scientist", 7, "epic"),
        Option("Гоблин-копирайтер", "goblin", 7, "epic"),
        Option("Уставший саппорт", "tired_support", 10, "common"),
        Option("Кринжовый инфлюенсер", "influencer", 8, "rare"),
        Option("Нуарный детектив", "noir_detective", 7, "rare"),
        Option("Безумный профессор", "mad_professor", 5, "epic"),
        Option("Древний оракул", "oracle", 4, "epic"),
        Option("Финальный босс", "final_boss", 4, "legendary"),
    ),
    "format": (
        Option("Обычный текст", "plain", 25, "common"),
        Option("Чек-лист", "checklist", 16, "common"),
        Option("Таблица", "table", 11, "rare"),
        Option("JSON", "json", 8, "epic"),
        Option("Диалог двух экспертов", "dialogue", 8, "epic"),
        Option("Терминальный лог", "terminal", 8, "rare"),
        Option("Пошаговый квест", "quest", 8, "rare"),
        Option("Карточки фактов", "cards", 7, "rare"),
        Option("Хайку", "haiku", 4, "legendary"),
        Option("Патчноут", "patch_notes", 5, "epic"),
    ),
    "language": (
        Option("Русский", "ru", 39, "common"),
        Option("English", "en", 19, "common"),
        Option("中文", "zh", 8, "rare"),
        Option("Deutsch", "de", 7, "rare"),
        Option("Español", "es", 6, "rare"),
        Option("Français", "fr", 6, "rare"),
        Option("Português", "pt", 5, "epic"),
        Option("한국어", "ko", 4, "epic"),
        Option("العربية", "ar", 3, "epic"),
        Option("日本語", "ja", 3, "legendary"),
    ),
    "chaos": (
        Option("Без мутаций", "none", 25, "common"),
        Option("Не больше 50 слов", "max_50_words", 11, "common"),
        Option("Добавляй эмодзи", "emoji", 9, "rare"),
        Option("Только короткие предложения", "short_sentences", 9, "rare"),
        Option("Закончи неожиданным выводом", "plot_twist", 7, "epic"),
        Option("Отвечай только вопросами", "questions_only", 4, "legendary"),
        Option("Объясняй через котов", "cats", 8, "rare"),
        Option("Каждый пункт всё страннее", "escalating_weirdness", 6, "epic"),
        Option("Не используй букву А", "no_letter_a", 3, "legendary"),
        Option("Добавь бесполезный факт", "useless_fact", 6, "rare"),
        Option("Спорь сам с собой", "self_debate", 5, "epic"),
        Option("Начни с конца", "reverse_order", 4, "epic"),
        Option("Рифмуй ключевые мысли", "rhyming", 2, "legendary"),
        Option("Используй игровую терминологию", "gaming_terms", 7, "common"),
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
