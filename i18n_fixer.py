import os

RU_FILE = "backend/locale/ru/LC_MESSAGES/django.po"
EN_FILE = "backend/locale/en/LC_MESSAGES/django.po"

translations = {
    "Bittada Mebel Ecosystem": {"ru": "Экосистема Мебели Bittada", "en": "Bittada Furniture Ecosystem"},
    "Mebellar va": {"ru": "Мебель и", "en": "Furniture and"},
    "usta dizaynerlar": {"ru": "мастера дизайнеры", "en": "master designers"},
    "bir joyda": {"ru": "в одном месте", "en": "in one place"},
    "O'zbekistondagi eng yirik platforma. 1000+ ishlab chiqaruvchi va tayyor mebellar katalogi. B2B va B2C uchun yagona yechim.": {
        "ru": "Крупнейшая платформа в Узбекистане. Каталог 1000+ производителей и готовой мебели. Единое решение для B2B и B2C.",
        "en": "The largest platform in Uzbekistan. Catalog of 1000+ manufacturers and ready-made furniture. A single solution for B2B and B2C."
    },
    "Xizmatlarni ko'rish": {"ru": "Посмотреть услуги", "en": "View Services"},
    "Ustalar izlash": {"ru": "Поиск мастеров", "en": "Find Masters"},
    "Nimani qidiryapsiz?...": {"ru": "Что вы ищете?...", "en": "What are you looking for?..."},
    "Qidirish": {"ru": "Поиск", "en": "Search"},
}

def update_po_file(filepath, lang):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    for msgid, trans_dict in translations.items():
        trans_str = trans_dict.get(lang, "")
        if f'msgid "{msgid}"' not in content:
            # Append if not exists
            content += f'\n\nmsgid "{msgid}"\nmsgstr "{trans_str}"\n'
        else:
            # Replace empty msgstr if it exists
            # This is a simple replace and might not cover all cases, but works for our specific new strings
            part1 = f'msgid "{msgid}"\nmsgstr ""'
            part2 = f'msgid "{msgid}"\nmsgstr "{trans_str}"'
            content = content.replace(part1, part2)
            
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {filepath}")

if __name__ == "__main__":
    update_po_file(RU_FILE, "ru")
    update_po_file(EN_FILE, "en")
    print("\n[SUCCESS] Translations injected. Now run:")
    print("cd backend && python manage.py compilemessages")
