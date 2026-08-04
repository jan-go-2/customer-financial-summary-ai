import json
import logging
import logging.handlers
import os
import re
import sys
from pathlib import Path

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.environ.get("LOG_FORMAT", "text")
LOG_DIR = Path(os.environ.get("LOG_DIR", "logs"))
LOG_FILE = LOG_DIR / "app.log"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB per file
LOG_BACKUP_COUNT = 5              # keep last 5 rotated files


_PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
_AADHAAR_PATTERN = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")


def _redact(text: str) -> str:
    text = _PAN_PATTERN.sub("[REDACTED_PAN]", text)
    text = _AADHAAR_PATTERN.sub("[REDACTED_AADHAAR]", text)
    return text


class RedactionFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = _redact(record.msg)
        return True


class RunContextFilter(logging.Filter):
    """Guarantees run_id/doc_file always exist on a record, even if a log
    call forgot to pass extra=, so the formatter never crashes on a missing
    key."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "run_id"):
            record.run_id = "-"
        if not hasattr(record, "doc_file"):
            record.doc_file = "-"
        return True


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

TEXT_FORMAT = (
    "%(asctime)s | %(levelname)-8s | run=%(run_id)s | "
    "%(name)s:%(funcName)s:%(lineno)d | %(message)s"
)


class JsonFormatter(logging.Formatter):
    """One JSON object per line -- queryable in CloudWatch/Datadog/Loki/ELK,
    instead of grepping text."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName,
            "message": record.getMessage(),
            "run_id": getattr(record, "run_id", "-"),
            "doc_file": getattr(record, "doc_file", "-"),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def setup_logging(level: str = LOG_LEVEL, log_format: str = LOG_FORMAT) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = JsonFormatter() if log_format == "json" else logging.Formatter(TEXT_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Switch to TimedRotatingFileHandler(..., when="midnight", backupCount=14)
    # if you'd rather rotate daily than by file size.
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()  # avoid duplicate handlers on reload (e.g. uvicorn --reload)
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    for f in (RedactionFilter(), RunContextFilter()):
        console_handler.addFilter(f)
        file_handler.addFilter(f)

    # Quiet noisy third-party libraries so they don't drown out your own logs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("docling").setLevel(logging.WARNING)

    logging.getLogger(__name__).info("Logging initialized")