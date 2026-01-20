from datetime import datetime, timezone


def utcnow_dt() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def dt_from_unix_ms(unix_ms: int) -> datetime:
    return datetime.fromtimestamp(unix_ms / 1000, tz=timezone.utc).replace(tzinfo=None)

def parse_iso_z_to_naive(iso_z: str) -> datetime:
    # "2026-01-20T19:05:23.275Z" -> aware UTC -> naive UTC
    # fromisoformat не понимает 'Z', заменяем на '+00:00'
    dt = datetime.fromisoformat(iso_z.replace("Z", "+00:00"))
    return dt.astimezone(timezone.utc).replace(tzinfo=None)