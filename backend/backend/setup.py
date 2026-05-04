"""
Bittada backend — birinchi marta sozlash skripti.

Foydalanish:
    python setup.py            # hammasi: secret + db + migrate
    python setup.py secret     # faqat DJANGO_SECRET_KEY ni yangilash
    python setup.py migrate    # faqat makemigrations + migrate
    python setup.py reset_db   # DB ni tozalash + qayta migrate (TEST DATA YO'QOLADI)

Bu skript uchun talablar:
    - Python 3.12+ va virtualenv aktiv
    - PostgreSQL ishlayapti (localhost:5432)
    - Redis ishlayapti (localhost:6379)
    - paketlar o'rnatilgan: pip install -r requirements/dev.txt
"""
from __future__ import annotations

import os
import secrets
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
ENV_FILE = ROOT_DIR / ".env"
ENV_EXAMPLE = ROOT_DIR / ".env.example"


def colored(msg: str, color: str = "blue") -> str:
    codes = {"blue": "\033[1;34m", "green": "\033[1;32m", "red": "\033[1;31m"}
    return f"{codes.get(color, '')}{msg}\033[0m"


def log(msg: str) -> None:
    print(colored(f"▸ {msg}", "blue"))


def ok(msg: str) -> None:
    print(colored(f"✓ {msg}", "green"))


def fail(msg: str) -> None:
    print(colored(f"✗ {msg}", "red"), file=sys.stderr)
    sys.exit(1)


def ensure_env_file() -> None:
    """`.env` mavjud bo'lmasa, `.env.example` dan ko'chiramiz."""
    if ENV_FILE.exists():
        return
    if not ENV_EXAMPLE.exists():
        fail(f"{ENV_EXAMPLE} topilmadi.")
    log(f".env yaratilmoqda ({ENV_EXAMPLE.name} dan)")
    ENV_FILE.write_text(ENV_EXAMPLE.read_text())
    ok(".env yaratildi")


def update_env_var(key: str, value: str) -> None:
    """`.env` ichidagi bitta o'zgaruvchini yangilaydi (mavjud bo'lsa) yoki qo'shadi."""
    text = ENV_FILE.read_text()
    lines = text.splitlines()
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}")
    ENV_FILE.write_text("\n".join(lines) + "\n")


def load_env() -> None:
    """`.env` ni `os.environ` ga yuklaydi (dotenv ishlatmasdan, oddiy parser)."""
    if not ENV_FILE.exists():
        return
    for raw in ENV_FILE.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        # qiymat tirnoq bilan o'ralgan bo'lsa olib tashlaymiz
        val = val.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), val)


def cmd_secret() -> None:
    """Yangi DJANGO_SECRET_KEY yaratib `.env` ga yozadi."""
    ensure_env_file()
    new = secrets.token_urlsafe(50)
    update_env_var("DJANGO_SECRET_KEY", new)
    ok("DJANGO_SECRET_KEY yangilandi")


def check_postgres() -> None:
    """psycopg orqali postgres ga ulanishni tekshiradi."""
    try:
        import psycopg
    except ImportError:
        fail("psycopg o'rnatilmagan. Avval: pip install -r requirements/dev.txt")

    log("PostgreSQL ulanishini tekshirish")
    dsn = (
        f"dbname={os.environ['POSTGRES_DB']} "
        f"user={os.environ['POSTGRES_USER']} "
        f"password={os.environ['POSTGRES_PASSWORD']} "
        f"host={os.environ['POSTGRES_HOST']} "
        f"port={os.environ['POSTGRES_PORT']}"
    )
    try:
        with psycopg.connect(dsn, connect_timeout=3) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        ok(f"postgres {os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']} OK")
    except psycopg.OperationalError as exc:
        fail(
            f"PostgreSQL ga ulanmadi: {exc}\n\n"
            f"Quyidagi buyruqlar bilan tuzating:\n"
            f"  sudo systemctl start postgresql\n"
            f"  sudo -u postgres psql -c \"CREATE USER {os.environ['POSTGRES_USER']} "
            f"WITH PASSWORD '{os.environ['POSTGRES_PASSWORD']}' CREATEDB;\"\n"
            f"  sudo -u postgres psql -c \"CREATE DATABASE {os.environ['POSTGRES_DB']} "
            f"OWNER {os.environ['POSTGRES_USER']};\""
        )


def check_redis() -> None:
    try:
        import redis
    except ImportError:
        fail("redis paketi o'rnatilmagan.")
    log("Redis ulanishini tekshirish")
    try:
        r = redis.Redis.from_url(os.environ["REDIS_URL"], socket_connect_timeout=2)
        r.ping()
        ok(f"redis {os.environ['REDIS_URL']} OK")
    except Exception as exc:
        fail(f"Redis ga ulanmadi: {exc}\n  sudo systemctl start redis-server")


def run_django(*args: str) -> None:
    """`python manage.py ...` ni shu interpretator bilan ishga tushiradi."""
    cmd = [sys.executable, "manage.py", *args]
    print(colored(f"  $ {' '.join(cmd)}", "blue"))
    result = subprocess.run(cmd, cwd=BACKEND_DIR)
    if result.returncode != 0:
        fail(f"manage.py {args[0]} xato bilan tugadi (exit {result.returncode})")


def cmd_migrate() -> None:
    load_env()
    check_postgres()
    log("Migratsiyalar")
    run_django("makemigrations", "users", "auth_methods", "security", "--no-input")
    run_django("migrate", "--no-input")
    ok("migratsiyalar qo'llandi")


def cmd_reset_db() -> None:
    load_env()
    log("DB ni qayta yaratish (eski ma'lumotlar yo'qoladi)")
    run_django("flush", "--no-input")
    cmd_migrate()


def cmd_all() -> None:
    ensure_env_file()
    load_env()

    if os.environ.get("DJANGO_SECRET_KEY", "").startswith("replace-me"):
        cmd_secret()
        load_env()  # qayta yuklaymiz

    check_postgres()
    check_redis()
    cmd_migrate()

    print()
    ok("Setup tugadi!")
    print()
    print("Keyingi qadamlar:")
    print(f"  {colored('python manage.py createsuperuser', 'blue')}    # admin yaratish")
    print(f"  {colored('python manage.py runserver',     'blue')}      # dev server (8000)")
    print(f"  {colored('python -m daphne -b 0.0.0.0 -p 8001 config.asgi:application', 'blue')}  # WebSocket")
    print(f"  {colored('celery -A config worker -l INFO', 'blue')}     # Celery worker")
    print()


COMMANDS = {
    "all":      cmd_all,
    "secret":   cmd_secret,
    "migrate":  cmd_migrate,
    "reset_db": cmd_reset_db,
}


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    fn = COMMANDS.get(cmd)
    if not fn:
        print(f"Noma'lum buyruq: {cmd}\nFoydalanish: python setup.py [{' | '.join(COMMANDS)}]")
        sys.exit(1)
    fn()
