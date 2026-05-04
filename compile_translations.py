#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bittada Marketplace — i18n .po → .mo kompilyatori
====================================================
Pure-Python qator-faylli msgfmt — Django'ning compilemessages buyrug'i sayozimi
(GNU gettext + msgfmt o'rniga) — har qanday muhitda ishlaydi.

Foydalanish:
    python compile_translations.py

Buyruq backend/locale/<lang>/LC_MESSAGES/django.po fayllarini o'qiydi va
har biri uchun yondosh django.mo (binar GNU MO format) yaratadi.

Lokalizatsiya pipeline:
    1) Templatelarda {% trans "..." %} taglar qo'yiladi (loyihada qilingan).
    2) Tarjimalar backend/locale/{ru,en}/LC_MESSAGES/django.po faylida.
    3) Bu skript .po → .mo ga aylantiradi (Django shu .mo dan o'qiydi).
    4) Server qayta yoqilganda yangi tarjimalar ko'rinadi.
"""
# Standart kutubxona modullari — qo'shimcha bog'liqliklar yo'q (faqat Python)
import os
import struct
import sys
from pathlib import Path

# Loyiha ildizidagi locale katalogi (backend/locale/<lang>/LC_MESSAGES/)
BASE_DIR = Path(__file__).resolve().parent
LOCALE_DIR = BASE_DIR / "backend" / "locale"


def parse_po(po_path: Path) -> dict[str, str]:
    """
    .po faylini o'qib, msgid → msgstr lug'atini qaytaradi.
    Oddiy parser: ko'p qatorli msgid/msgstr, escape sequencelarni qo'llaydi.
    """
    # Tarjimalarni saqlovchi lug'at — "" (header) ham keyinchalik kerak
    translations: dict[str, str] = {}
    # Faylni UTF-8 sifatida o'qiymiz (PO fayllar har doim UTF-8 bo'lishi shart)
    text = po_path.read_text(encoding="utf-8")

    # Joriy holat: msgid yig'ilyapti, msgstr yig'ilyapti yoki none
    msgid_lines: list[str] = []
    msgstr_lines: list[str] = []
    state = None  # None | "msgid" | "msgstr"

    def flush() -> None:
        # Tugagan blokni lug'atga qo'shamiz (agar ikkala qism mavjud bo'lsa)
        if msgid_lines is not None and msgstr_lines is not None:
            msgid = "".join(msgid_lines)
            msgstr = "".join(msgstr_lines)
            # Faqat msgstr bo'sh bo'lmagan tarjimalarnigina qo'shamiz
            # (header msgid="" maxsus holat — uni ham qo'shamiz)
            if msgstr or msgid == "":
                translations[msgid] = msgstr

    # PO fayl qatorlari ustida yuramiz
    for raw_line in text.splitlines():
        # Bo'shliqlarni olib tashlangan holatda boshlanadigan kalit so'zga qaraymiz
        line = raw_line.rstrip()

        # Izoh qatorlari (# bilan boshlanadi) — e'tiborga olmaymiz
        if line.startswith("#"):
            continue

        # Yangi msgid bloki boshlandi → eskisini yozib tashlaymiz
        if line.startswith("msgid "):
            # Avvalgi blokni saqlash
            if state is not None:
                flush()
            # Yangi blokni boshlaymiz
            msgid_lines = []
            msgstr_lines = []
            state = "msgid"
            # Birinchi qator qiymatini ajratib olamiz: msgid "..."
            msgid_lines.append(_unescape(line[6:].strip()))
            continue

        # msgstr boshlandi
        if line.startswith("msgstr "):
            state = "msgstr"
            msgstr_lines.append(_unescape(line[7:].strip()))
            continue

        # Davomi (qo'shtirnoq ichida): msgid yoki msgstr ga qo'shamiz
        if line.startswith('"') and line.endswith('"'):
            if state == "msgid":
                msgid_lines.append(_unescape(line))
            elif state == "msgstr":
                msgstr_lines.append(_unescape(line))
            continue

        # Bo'sh qator — blokni yakunlaydi
        if line == "":
            if state is not None:
                flush()
                msgid_lines = []
                msgstr_lines = []
                state = None
            continue

    # Fayl oxiridagi blokni yozib tashlaymiz
    if state is not None:
        flush()

    return translations


def _unescape(quoted: str) -> str:
    """
    Qo'shtirnoqlar ichidagi C-style stringni Python stringga o'tkazadi.
    Misol: '"Salom\\n"' → 'Salom\n'
    """
    # Boshlanish/oxirgi qo'shtirnoqlarni olib tashlash
    if quoted.startswith('"'):
        quoted = quoted[1:]
    if quoted.endswith('"'):
        quoted = quoted[:-1]
    # Asosiy escape ketma-ketliklarni almashtirish (gettext PO formatida)
    return (
        quoted.replace('\\n', '\n')
        .replace('\\t', '\t')
        .replace('\\r', '\r')
        .replace('\\"', '"')
        .replace('\\\\', '\\')
    )


def write_mo(translations: dict[str, str], mo_path: Path) -> None:
    """
    Tarjimalar lug'atidan GNU MO format binar faylni yozadi.
    Format hujjati: https://www.gnu.org/software/gettext/manual/html_node/MO-Files.html
    """
    # Mahsulot kalitlari (key) ni alfavit tartibida saralash (MO format talabi)
    keys = sorted(translations.keys())
    # Har bir kalit va qiymatni UTF-8 baytga aylantirish
    keys_bytes = [k.encode("utf-8") for k in keys]
    values_bytes = [translations[k].encode("utf-8") for k in keys]

    # Yozuvlar soni (header bilan birga)
    n = len(keys)
    # Header — 7 ta 32-bit kattalik (28 bayt)
    header_size = 7 * 4
    # Indeks jadvallari — har biri n ta yozuv × (4 bayt uzunlik + 4 bayt offset) = 8n bayt
    table_size = n * 4 * 2

    # Stringlar bloki boshlanadigan offset — header VA IKKI jadvaldan (orig + trans) keyin
    # MUHIM: 2 * table_size, chunki MO formatida msgid jadvali va msgstr jadvali alohida.
    offset_keys = header_size + 2 * table_size
    # Kalitlar uzunligi va offsetlari ro'yxati
    keys_offsets: list[tuple[int, int]] = []
    cur = offset_keys
    keys_blob = b""
    for kb in keys_bytes:
        # Har bir string \0 bilan tugaydi (lekin uzunlikka kirmaydi)
        keys_offsets.append((len(kb), cur))
        keys_blob += kb + b"\0"
        cur += len(kb) + 1

    offset_values = cur
    values_offsets: list[tuple[int, int]] = []
    values_blob = b""
    for vb in values_bytes:
        values_offsets.append((len(vb), cur))
        values_blob += vb + b"\0"
        cur += len(vb) + 1

    # Header yozish — magic + version + N + offset_orig_table + offset_trans_table
    # + hash_size (0) + hash_offset (0)
    output = struct.pack(
        "Iiiiiii",
        0x950412DE,        # MO faylining sehrli raqami
        0,                 # Versiya
        n,                 # Yozuvlar soni
        header_size,       # Asl stringlar jadvali offset
        header_size + n * 8,  # Tarjima stringlari jadvali offset
        0,                 # Hash jadvali kattaligi (ishlatmaymiz)
        0,                 # Hash jadvali offseti
    )

    # Asl stringlar (keys) jadvali
    for length, offset in keys_offsets:
        output += struct.pack("ii", length, offset)
    # Tarjima stringlari (values) jadvali
    for length, offset in values_offsets:
        output += struct.pack("ii", length, offset)
    # Stringlar bloki
    output += keys_blob + values_blob

    # Faylga yozish (binary mode)
    mo_path.write_bytes(output)


def compile_locale(lang: str) -> bool:
    """
    Bitta til uchun .po → .mo kompilyatsiyasi.
    True qaytaradi muvaffaqiyatli bo'lganda, False — fayl topilmasa.
    """
    # PO va MO fayl yo'llari
    po_path = LOCALE_DIR / lang / "LC_MESSAGES" / "django.po"
    mo_path = LOCALE_DIR / lang / "LC_MESSAGES" / "django.mo"

    # PO fayl mavjudligini tekshirish
    if not po_path.exists():
        print(f"  [SKIP] {po_path} topilmadi")
        return False

    # PO faylni parse qilish
    translations = parse_po(po_path)
    print(f"  [{lang}] {len(translations)} ta yozuv topildi")

    # MO faylga yozish
    write_mo(translations, mo_path)
    print(f"  [OK]   {mo_path} yozildi ({mo_path.stat().st_size} bayt)")
    return True


def main() -> int:
    """Asosiy nuqta — barcha tillarni kompilyatsiya qilish."""
    # Locale katalogi mavjudligini tekshirish
    if not LOCALE_DIR.exists():
        print(f"XATOLIK: locale katalogi topilmadi: {LOCALE_DIR}")
        return 1

    # Mavjud tillarni topish (uz, ru, en va h.k.)
    languages = sorted(d.name for d in LOCALE_DIR.iterdir() if d.is_dir())
    print(f"Topilgan tillar: {', '.join(languages)}")

    # Har bir til uchun kompilyatsiya
    success = 0
    for lang in languages:
        print(f"\n→ {lang} tilini kompilyatsiya qilyapman...")
        if compile_locale(lang):
            success += 1

    # Yakuniy xulosa
    print(f"\n[YAKUN] {success}/{len(languages)} til muvaffaqiyatli kompilyatsiya qilindi")
    print("Endi serverni qayta ishga tushiring (yoki autoreload uni ko'radi).")
    return 0 if success > 0 else 1


# Skriptni to'g'ridan-to'g'ri ishga tushirilganda main() chaqiriladi
if __name__ == "__main__":
    sys.exit(main())
