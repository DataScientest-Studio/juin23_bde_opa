from datetime import timedelta
from pathlib import Path

from loguru import logger

from opa import settings


def get_session():
    if settings.use_http_cache:
        import requests_cache
        from requests_cache.models.response import CachedResponse
        from requests_cache.backends.sqlite import SQLiteCache

        return requests_cache.CachedSession(
            "opa",
            backend=SQLiteCache(db_path=Path(settings.http_cache_dir) / "opa"),
            # This should certainly be set by request, but within the limited scope of this
            # project, new data is fetched every day, and the API rate is limited anyway.
            # Hardcoding the value is good enough.
            expire_after=timedelta(hours=12.0),
        )
    else:
        import requests

        return requests.Session()


def is_cached(request):
    try:
        return request.from_cache
    except AttributeError:
        return False


session = get_session()


def get_json_data(url: str, **kwargs):
    http = session.get(url, **kwargs)
    status = http.status_code

    if status >= 300:
        raise RuntimeError(f"Got unhandled response code={status} : {http.json()}")

    logger.debug(
        "Got successful HTTP response from {cached}{url}",
        cached="cached " if is_cached(http) else "",
        url=http.url,
    )

    return http.json()
