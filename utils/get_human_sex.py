def get_sex_human(sex: str) -> str:
    mapping = {
        "man": "Мужчина",
        "woman": "Женщина"
    }
    return mapping.get(sex, "Не определен")
