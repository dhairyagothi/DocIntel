from normalization.numbers import normalize_number
from normalization.dates import normalize_period


def test_crore_and_million_normalize_to_same_amount():
    assert normalize_number("25 crore")["amount"] == normalize_number("250 million")["amount"]


def test_fiscal_period_normalization():
    assert normalize_period("Q4 FY25") == {"fiscal_year": 2025, "quarter": 4}