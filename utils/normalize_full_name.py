import re

FULL_NAME_RE = re.compile(r"^[а-яА-Я]+(?: [а-яА-Я]+)*$")


def normalize_full_name(raw: str | None) -> str | None:
    if raw and len(raw.split()) >= 2 and len(raw) < 100 and bool(FULL_NAME_RE.fullmatch(raw)):
        return raw
