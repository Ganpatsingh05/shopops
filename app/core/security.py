from secrets import compare_digest

from fastapi import Header, HTTPException, status

from app.core.config import settings


def require_admin_api_key(
    x_admin_api_key: str | None = Header(default=None),
) -> None:
    if not x_admin_api_key or not compare_digest(
        x_admin_api_key,
        settings.admin_api_key,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin API key",
        )
    