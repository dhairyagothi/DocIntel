from normalization.numbers import SCALE


def normalize_unit(unit: str | None) -> str | None:
    if not unit:
        return None
    value = unit.strip().lower()
    aliases = {"mn": "million", "m": "million", "bn": "billion", "cr": "crore", "k": "thousand"}
    return aliases.get(value, value)


def unit_multiplier(unit: str | None) -> float:
    return SCALE.get((unit or "").lower(), 1)