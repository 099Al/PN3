from datetime import datetime, timezone


def utcnow_dt() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def dt_from_unix_ms(unix_ms: int) -> datetime:
    return datetime.fromtimestamp(unix_ms / 1000, tz=timezone.utc).replace(tzinfo=None)