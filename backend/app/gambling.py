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
    adult: bool = False
    token_burn: bool = False


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
        Option("Без мутаций", "none", 12, "common"),
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
        Option("Пост бати в Одноклассниках", "dad_social", 5, "rare"),
        Option("Голосовуха на 7 минут", "voice_note", 5, "rare"),
        Option("Внезапная реклама", "fake_ad", 4, "epic"),
        Option("Диалог с NPC", "npc_dialogue", 5, "rare"),
        Option("Теория заговора", "conspiracy", 4, "epic"),
        Option("КАПСЛОК ЗАЛИП", "caps_lock", 3, "epic"),
        Option("Всё уменьшительно-ласкательно", "diminutives", 4, "epic"),
        Option("Термины заменить на еду", "food_terms", 5, "rare"),
        Option("Добавь подозрительную утку", "suspicious_duck", 3, "legendary"),
        Option("Неловкий свадебный тост", "awkward_toast", 4, "epic"),
        Option("Продавец с маркетплейса", "marketplace_seller", 5, "rare"),
        Option("Ответ-гороскоп", "horoscope", 4, "epic"),
        Option("Кликбейт из 2012-го", "clickbait", 4, "epic"),
        Option("Нейросетевой брейнрот", "brainrot", 3, "legendary"),
        Option("Бюрократический кошмар", "bureaucratic", 5, "rare"),
        Option("Каждую фразу заканчивай «брат»", "bro_every_sentence", 3, "epic"),
        Option("Драматические паузы...", "dramatic_pauses", 5, "rare"),
        Option("Сигнал повреждён", "corrupted_signal", 3, "legendary"),
        Option("Объясни как бывшему", "ex_explanation", 4, "epic"),
        Option("Спортивный комментатор", "sports_commentator", 5, "rare"),
        Option("Утренник в детсаду", "kindergarten", 4, "epic"),
        Option("Спонсор — шаурма у вокзала", "shawarma_sponsor", 3, "legendary"),
        Option("Мотивационный коуч", "motivational_coach", 5, "rare"),
        Option("Бабушкин рецепт", "grandma_recipe", 4, "epic"),
        Option("Отзыв на одну звезду", "one_star_review", 4, "epic"),
        Option("Судебное заседание", "courtroom", 4, "epic"),
        Option("Цензурь случайные слова", "random_censorship", 3, "legendary"),
        Option("Мыльная опера", "soap_opera", 4, "epic"),
        Option("С матом, но по делу", "profanity_light", 6, "rare", adult=True),
        Option("Мат через слово", "profanity_heavy", 3, "legendary", adult=True),
        Option("Пьяный дядя на кухне", "drunk_uncle", 5, "epic", adult=True),
        Option("Жёсткая прожарка", "brutal_roast", 4, "epic", adult=True),
        Option("Чёрный юмор", "dark_humor", 4, "epic", adult=True),
        Option("Саппорт окончательно сорвался", "support_snapped", 4, "epic", adult=True),
        Option("Злой таксист объясняет жизнь", "angry_taxi", 4, "epic", adult=True),
        Option("Матерный поэт", "filthy_poet", 3, "legendary", adult=True),
        Option("ПУСТОЙ ПРОКРУТ", "token_burn", 2, "legendary", token_burn=True),
    ),
}


class GamblingEngine:
    def roll(
        self,
        seed: str | None = None,
        *,
        adult_mode: bool = False,
        allow_token_burn: bool = False,
    ) -> tuple[str, list[RollItem]]:
        seed = seed or secrets.token_hex(16)
        rng = random.Random(seed)
        results: list[RollItem] = []
        for category, options in TABLES.items():
            available = [
                item
                for item in options
                if (adult_mode or not item.adult)
                and (allow_token_burn or not item.token_burn)
            ]
            option = rng.choices(available, weights=[item.weight for item in available], k=1)[0]
            results.append(
                RollItem(
                    category=category,
                    label=option.label,
                    value=option.value,
                    rarity=option.rarity,  # type: ignore[arg-type]
                )
            )
        return seed, results
