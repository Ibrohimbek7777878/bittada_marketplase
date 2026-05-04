#!/usr/bin/env python
"""
Fix translations script for Bittada Marketplace.
This script fixes common i18n issues:
1. Removes empty/corrupted .mo files
2. Recompiles .po files to .mo files
3. Fixes duplicate msgid entries in .po files
"""

import os
import subprocess
import sys
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
sys.path.insert(0, str(Path(__file__).parent))


def fix_po_duplicates(po_file):
    """Remove duplicate msgid entries from .po file."""
    print(f"Checking {po_file} for duplicates...")

    with open(po_file, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    seen_msgids = {}
    output = []
    skip_until_next = False
    current_msgid = None

    for line in lines:
        if line.startswith('msgid "'):
            msgid = line[7:-1]  # Extract msgid value
            if msgid in seen_msgids:
                # Duplicate found, skip this entry
                skip_until_next = True
                print(f"  Removing duplicate: {msgid[:50]}...")
                continue
            else:
                seen_msgids[msgid] = True
                skip_until_next = False

        if skip_until_next:
            if line.startswith('#:') or line.startswith('msgstr'):
                continue
            if line.strip() == '' or line.startswith('#:'):
                skip_until_next = False

        if not skip_until_next:
            output.append(line)

    with open(po_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"  Done.")


def clean_mo_files():
    """Remove all .mo files."""
    base_dir = Path(__file__).parent
    locale_dir = base_dir / 'locale'

    print("Cleaning .mo files...")
    for mo_file in locale_dir.rglob('*.mo'):
        print(f"  Removing {mo_file}")
        mo_file.unlink()


def compile_messages():
    """Compile .po files to .mo files."""
    base_dir = Path(__file__).parent
    locale_dir = base_dir / 'locale'

    print("Compiling messages...")
    for po_file in locale_dir.rglob('*.po'):
        mo_file = po_file.with_suffix('.mo')

        # Check if .po file is valid
        try:
            result = subprocess.run(
                ['msgfmt', '--check-format', str(po_file)],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"  Error in {po_file}: {result.stderr}")
                continue
        except FileNotFoundError:
            print("  Warning: msgfmt not found. Installing gettext-tools may be needed.")

        # Compile .po to .mo
        result = subprocess.run(
            ['msgfmt', str(po_file), '-o', str(mo_file)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            size = mo_file.stat().st_size if mo_file.exists() else 0
            print(f"  Created {mo_file} ({size} bytes)")
        else:
            print(f"  Failed to compile {po_file}: {result.stderr}")


def test_translations():
    """Test if translations are working."""
    import django
    django.setup()

    from django.utils.translation import activate, gettext

    print("\nTesting translations...")

    tests = [
        ('ru', 'Katalog', 'Каталог'),
        ('ru', 'Mebellar', 'Мебель'),
        ('uz', 'Katalog', 'Katalog'),
        ('en', 'Katalog', 'Catalog'),
    ]

    all_passed = True
    for lang, msgid, expected in tests:
        activate(lang)
        result = gettext(msgid)
        passed = result == expected
        status = "✓" if passed else "✗"
        print(f"  {status} [{lang}] {msgid} -> {result} (expected: {expected})")
        if not passed:
            all_passed = False

    return all_passed


def main():
    print("=" * 60)
    print("Bittada Marketplace - Translation Fix Script")
    print("=" * 60)

    # Step 1: Clean .mo files
    clean_mo_files()

    # Step 2: Fix duplicates in .po files
    base_dir = Path(__file__).parent
    locale_dir = base_dir / 'locale'

    for po_file in locale_dir.rglob('*.po'):
        fix_po_duplicates(po_file)

    # Step 3: Compile messages
    compile_messages()

    # Step 4: Test translations
    try:
        if test_translations():
            print("\n✓ All translations are working correctly!")
            return 0
        else:
            print("\n✗ Some translations are not working.")
            return 1
    except Exception as e:
        print(f"\n✗ Error testing translations: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
