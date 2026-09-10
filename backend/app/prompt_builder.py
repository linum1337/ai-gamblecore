from app.schemas import RollItem


QUALITY = {
    "catastrophic": "Give a chaotic, obviously flawed answer with gaps and dubious shortcuts, but do not fabricate dangerous facts.",
    "low": "Give a deliberately shallow answer with minimal reasoning.",
    "rushed": "Answer as if only five minutes remain: prioritize speed and the bare essentials.",
    "normal": "Give a useful but concise answer.",
    "high": "Give a careful, well-reasoned and detailed answer.",
    "maximum": "Produce the best possible answer: rigorous, insightful, and polished.",
    "obsessive": "Be obsessively precise, examine edge cases, and polish every detail.",
}
STYLES = {
    "neutral": "Use a neutral style.",
    "corporate": "Write like a corporate shaman mixing business jargon with mystical imagery.",
    "medieval": "Write like a medieval chronicler.",
    "toxic_reviewer": "Write like a harsh but technically accurate code reviewer. Do not insult protected groups.",
    "future_scientist": "Write like a scientist reporting from the year 3026.",
    "goblin": "Write like an excitable goblin copywriter.",
    "tired_support": "Write like an exhausted but competent technical support engineer near the end of a shift.",
    "influencer": "Write like an overenthusiastic, slightly cringe social media influencer.",
    "noir_detective": "Write like a hard-boiled noir detective narrating a case.",
    "mad_professor": "Write like an eccentric professor delighted by a dangerous-looking experiment.",
    "oracle": "Write like an ancient oracle using solemn and cryptic imagery while remaining useful.",
    "final_boss": "Write like the final boss delivering a formidable monologue before revealing the answer.",
}
FORMATS = {
    "plain": "Use normal prose.",
    "checklist": "Return a practical checklist.",
    "table": "Use a Markdown table where it helps.",
    "json": "Return valid JSON only.",
    "dialogue": "Present the answer as a dialogue between two experts who disagree.",
    "terminal": "Format the answer like a terminal session with commands, logs, and concise annotations.",
    "quest": "Present the answer as a step-by-step quest with objectives and checkpoints.",
    "cards": "Split the answer into compact titled fact cards.",
    "haiku": "Express the useful core as one or more haiku, preserving the requested language where possible.",
    "patch_notes": "Format the answer as software patch notes with Added, Changed, Fixed, and Known Issues sections where applicable.",
}
LANGUAGES = {
    "ru": "Russian",
    "en": "English",
    "zh": "Chinese",
    "de": "German",
    "es": "Spanish",
    "ja": "Japanese",
    "fr": "French",
    "pt": "Portuguese",
    "ko": "Korean",
    "ar": "Arabic",
}
CHAOS = {
    "none": "No additional constraint.",
    "max_50_words": "Use no more than 50 words.",
    "emoji": "Use relevant emoji throughout the answer.",
    "short_sentences": "Use only short sentences.",
    "plot_twist": "End with an unexpected but relevant conclusion.",
    "questions_only": "Every sentence must be a question.",
    "cats": "Explain the central ideas using cats as the recurring analogy.",
    "escalating_weirdness": "Make each successive section stranger than the previous one while staying relevant.",
    "no_letter_a": "Do not use the letter A in the response, including its lowercase form in the selected language where applicable.",
    "useless_fact": "Include one clearly labeled, harmless, and gloriously useless fact.",
    "self_debate": "Briefly argue against your own answer before giving the final position.",
    "reverse_order": "Present the conclusion first and then work backward to the premise.",
    "rhyming": "Make the key conclusions rhyme naturally.",
    "gaming_terms": "Use video-game terminology for progress, risks, and outcomes.",
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
