import re
from collections import Counter

from models.document import Document


def clean_document(document: Document) -> Document:
    lines_by_page = [[line.strip() for line in page.raw_text.splitlines() if line.strip()] for page in document.pages]
    repeated = Counter(line for lines in lines_by_page for line in lines if len(line) < 160)
    repeated_lines = {line for line, count in repeated.items() if count >= 3}
    for page, lines in zip(document.pages, lines_by_page):
        kept = []
        for line in lines:
            if line in repeated_lines and len(lines_by_page) > 2:
                continue
            if re.fullmatch(r"(page\s*)?\d+(\s*of\s*\d+)?", line, re.I):
                continue
            kept.append(line)
        page.clean_text = re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip()
    return document