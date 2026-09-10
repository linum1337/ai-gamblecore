from app.schemas import RollItem


QUALITY = {
    "low": "Give a deliberately shallow answer with minimal reasoning.",
    "normal": "Give a useful but concise answer.",
    "high": "Give a careful, well-reasoned and detailed answer.",
    "maximum": "Produce the best possible answer: rigorous, insightful, and polished.",
}
STYLES = {
    "neutral": "Use a neutral style.",
    "corporate": "Write like a corporate shaman mixing business jargon with mystical imagery.",
    "medieval": "Write like a medieval chronicler.",
    "toxic_reviewer": "Write like a harsh but technically accurate code reviewer. Do not insult protected groups.",
    "future_scientist": "Write like a scientist reporting from the year 3026.",
    "goblin": "Write like an excitable goblin copywriter.",
}
FORMATS = {
    "plain": "Use normal prose.",
    "checklist": "Return a practical checklist.",
    "table": "Use a Markdown table where it helps.",
    "json": "Return valid JSON only.",
    "dialogue": "Present the answer as a dialogue between two experts who disagree.",
}
LANGUAGES = {
    "ru": "Russian",
    "en": "English",
    "zh": "Chinese",
    "de": "German",
    "es": "Spanish",
    "ja": "Japanese",
}
CHAOS = {
    "none": "No additional constraint.",
    "max_50_words": "Use no more than 50 words.",
    "emoji": "Use relevant emoji throughout the answer.",
    "short_sentences": "Use only short sentences.",
    "plot_twist": "End with an unexpected but relevant conclusion.",
    "questions_only": "Every sentence must be a question.",
}


def as_map(rolls: list[RollItem]) -> dict[str, str]:
    return {item.category: item.value for item in rolls}


def build_final_prompt(prompt: str, rolls: list[RollItem]) -> str:
    selected = as_map(rolls)
    return "\n".join(
        (
            "Complete the user's task while following every modifier below.",
            f"Quality: {QUALITY[selected['quality']]}",
            f"Style: {STYLES[selected['style']]}",
            f"Format: {FORMATS[selected['format']]}",
            f"Response language: {LANGUAGES[selected['language']]}",
            f"Chaos rule: {CHAOS[selected['chaos']]}",
            "",
            "User task:",
            prompt,
        )
    )

