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
    "dad_social": "Write like an overly sincere dad posting on an old social network: awkward greeting, life lesson, and excessive punctuation.",
    "voice_note": "Write like a rambling seven-minute voice message transcript with digressions, self-corrections, and a useful conclusion.",
    "fake_ad": "Interrupt the answer once with a clearly fictional and absurd sponsor segment, then continue normally.",
    "npc_dialogue": "Frame the answer as dialogue options and responses from a slightly broken video-game NPC.",
    "conspiracy": "Connect the ideas like an overdramatic conspiracy board, while clearly keeping factual claims accurate.",
    "caps_lock": "WRITE THE ENTIRE RESPONSE IN UPPERCASE, EXCEPT CODE WHERE CASE MATTERS.",
    "diminutives": "Use comically excessive diminutive and affectionate word forms where the response language supports them.",
    "food_terms": "Replace key technical concepts with food analogies and explicitly map each food back to the real concept.",
    "suspicious_duck": "Include one suspicious duck that appears without explanation and somehow contributes to the conclusion.",
    "awkward_toast": "Deliver the answer as an increasingly awkward wedding toast while still completing the task.",
    "marketplace_seller": "Present the answer like an overconfident marketplace product listing with features, benefits, and one suspicious disclaimer.",
    "horoscope": "Present the answer as a horoscope whose predictions are actually practical recommendations.",
    "clickbait": "Use ridiculous 2012-era clickbait framing, but still provide the real answer; number seven may shock the reader.",
    "brainrot": "Use an intense but readable burst of current internet slang without slurs, harassment, or sexual content.",
    "bureaucratic": "Turn the answer into an absurd bureaucratic procedure with forms, approvals, stamps, and contradictory departments.",
    "bro_every_sentence": "End every prose sentence with the word 'брат' or its natural equivalent in the response language.",
    "dramatic_pauses": "Insert comically dramatic ellipses and stage pauses before important points.",
    "corrupted_signal": "Make the response look like a damaged transmission using occasional readable markers such as [SIGNAL LOST], repetitions, and glitches.",
    "ex_explanation": "Explain the answer like a tense message to an ex-partner: overly careful, defensive, but ultimately clear and respectful.",
    "sports_commentator": "Narrate the solution like an excited live sports commentator covering a decisive final match.",
    "kindergarten": "Present the answer like a chaotic kindergarten performance with simple props, roles, and an unexpectedly competent finale.",
    "shawarma_sponsor": "Include a clearly fictional sponsor message for a suspicious shawarma stand near a train station.",
    "motivational_coach": "Write like an excessively intense motivational coach who treats this small task as a life-changing breakthrough.",
    "grandma_recipe": "Explain the solution as a grandmother's recipe with ingredients, steps, and one family anecdote.",
    "one_star_review": "Frame the answer as a detailed one-star customer review that reluctantly admits what works.",
    "courtroom": "Stage the answer as a courtroom hearing with evidence, objections, and a final verdict.",
    "random_censorship": "Comically censor a few harmless ordinary words with asterisks, without obscuring critical information.",
    "soap_opera": "Turn the explanation into a melodramatic soap-opera scene full of betrayal, revelations, and a useful resolution.",
    "profanity_light": "Use natural Russian profanity occasionally for emphasis while remaining useful. Never direct abuse at the user or protected groups.",
    "profanity_heavy": "Use frequent expressive Russian profanity and an unfiltered tone, but keep the answer understandable and never attack the user or protected groups.",
    "drunk_uncle": "Write like a loud drunk uncle explaining the topic in a kitchen at 3 AM, with profanity, dubious metaphors, and a surprisingly solid conclusion.",
    "brutal_roast": "Roast the problem and bad approaches mercilessly with profanity, without humiliating the user or targeting protected traits.",
    "dark_humor": "Use dark, absurd humor and occasional profanity without encouraging harm or targeting real victims.",
    "support_snapped": "Write like technical support finally lost patience after the hundredth identical ticket: profane, exhausted, but technically correct.",
    "angry_taxi": "Explain like an angry taxi driver who has opinions about everything, uses profanity, and somehow knows the subject perfectly.",
    "filthy_poet": "Write as a profane street poet with rhythm, vivid metaphors, and a clear answer.",
    "token_burn": "Generate a complete, substantive answer up to 600 words. The application will intentionally discard it after generation.",
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
