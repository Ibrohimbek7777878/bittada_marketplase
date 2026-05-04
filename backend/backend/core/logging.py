"""Structured JSON log formatter — use in prod where logs are scraped to ELK/Loki."""
from __future__ import annotations

import json
import logging
import time


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        # Allow callers to add structured context via `logger.info("x", extra={"foo": 1})`.
        for k, v in record.__dict__.items():
            if k in payload or k.startswith("_") or k in {"args", "msg", "exc_info", "exc_text"}:
                continue
            if isinstance(v, (str, int, float, bool, list, dict, type(None))):
                payload[k] = v
        return json.dumps(payload, ensure_ascii=False)
