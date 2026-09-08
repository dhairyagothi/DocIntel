from __future__ import annotations

import re
from typing import Any

SCALE = {
    "k": 1_000,
    "thousand": 1_000,
    "million": 1_000_000,
    "mn": 1_000_000,
    "m": 1_000_000,
    "billion": 1_000_000_000,
    "bn": 1_000_000_000,
    "crore": 10_000_000,
    "cr": 10_000_000,
    "lakh": 100_000,
}
CURRENCIES = {"₹": "INR", "rs": "INR", "rs.": "INR", "inr": "INR", "$": "USD", "€": "EUR", "£": "GBP"}


def normalize_number(value: Any, unit: str | None = None, currency: str | None = None) -> dict[str, Any] | None:
    if isinstance(value, bool) or value is None:
        return None
    text = str(value).strip()
    match = re.search(r"(?i)(₹|rs\.?|inr|\$|€|£)?\s*(-?[\d][\d,]*(?:\.\d+)?)\s*(%|k|thousand|million|mn|m|billion|bn|crore|cr|lakh)?", text)
    if not match:
        try:
            return {"raw": text, "amount": float(text.replace(",", "")), "currency": currency, "scale": "absolute"}
        except ValueError:
            return None
    amount = float(match.group(2).replace(",", ""))
    detected_unit = (unit or match.group(3) or "").lower()
    if detected_unit in SCALE:
        amount *= SCALE[detected_unit]
    detected_currency = currency or CURRENCIES.get((match.group(1) or "").lower())
    return {
        "raw": text,
        "amount": amount,
        "currency": detected_currency,
        "scale": "percent" if detected_unit == "%" else "absolute",
    }