import re


def normalize_period(raw: str | None) -> dict[str, int | str] | None:
    if not raw:
        return None
    text = str(raw).strip().upper().replace(" ", "")
    quarter = re.search(r"Q([1-4])", text)
    year = re.search(r"(20\d{2})", text)
    short_year = re.search(r"FY'?(\d{2})$", text)
    if not year and short_year:
        year_value = 2000 + int(short_year.group(1))
    else:
        year_value = int(year.group(1)) if year else None
    if year_value:
        result: dict[str, int | str] = {"fiscal_year": year_value}
        if quarter:
            result["quarter"] = int(quarter.group(1))
        return result
    return {"raw": str(raw)}