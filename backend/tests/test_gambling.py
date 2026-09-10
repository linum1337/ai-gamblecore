from app.gambling import GamblingEngine, TABLES


def test_roll_contains_every_category() -> None:
    _, rolls = GamblingEngine().roll(seed="fixed-seed")
    assert {item.category for item in rolls} == set(TABLES)


def test_seed_makes_roll_deterministic() -> None:
    engine = GamblingEngine()
    assert engine.roll(seed="same-seed") == engine.roll(seed="same-seed")

