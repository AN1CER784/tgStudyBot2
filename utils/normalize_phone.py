import re

PHONE_RE = re.compile(r"^\+?\d{10,15}$")


def normalize_phone(raw: str | None) -> str | None:
    if raw and bool(PHONE_RE.fullmatch(raw)):
        digits = re.sub(r"\D", "", raw)
        if 10 <= len(digits) <= 15:
            return "+" + digits
