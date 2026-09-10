from app.gambling import GamblingEngine, TABLES
from app.prompt_builder import CHAOS, FORMATS, LANGUAGES, QUALITY, STYLES


def test_roll_contains_every_category() -> None:
    _, rolls = GamblingEngine().roll(seed="fixed-seed")
    assert {item.category for item in rolls} == set(TABLES)


def test_seed_makes_roll_deterministic() -> None:
    engine = GamblingEngine()
    assert engine.roll(seed="same-seed") == engine.roll(seed="same-seed")


def test_every_modifier_has_prompt_instruction() -> None:
    instructions = {
        "quality": QUALITY,
        "style": STYLES,
        "format": FORMATS,
        "language": LANGUAGES,
        "chaos": CHAOS,
    }

    for category, mapping in instructions.items():
        values = {option.value for option in TABLES[category]}
        assert values == set(mapping), f"Missing prompt instruction for {category}"


def test_chaos_pool_has_enough_variety() -> None:
    assert len(TABLES["chaos"]) >= 40


def test_restricted_rolls_are_opt_in() -> None:
    engine = GamblingEngine()
    adult_values = {option.value for option in TABLES["chaos"] if option.adult}

    for index in range(200):
        _, rolls = engine.roll(seed=f"safe-{index}")
        chaos = next(item for item in rolls if item.category == "chaos")
        assert chaos.value not in adult_values
        assert chaos.value != "token_burn"


def test_adult_pool_can_be_enabled() -> None:
    engine = GamblingEngine()
    adult_values = {option.value for option in TABLES["chaos"] if option.adult}
    seen = set()

    for index in range(500):
        _, rolls = engine.roll(seed=f"adult-{index}", adult_mode=True)
        seen.add(next(item.value for item in rolls if item.category == "chaos"))

    assert seen & adult_values
