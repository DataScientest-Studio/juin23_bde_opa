import requests
from datetime import timedelta
from pathlib import Path

from loguru import logger
import requests_cache
from requests_cache.models.response import CachedResponse
from requests_cache.backends.sqlite import SQLiteCache

from opa import settings


session = (
    requests_cache.CachedSession(
        "opa",
        backend=SQLiteCache(db_path=Path(settings.http_cache_dir) / "opa"),
        # This should certainly be set by request, but within the limited scope of this
        # project, new data is fetched every day, and the API rate is limited anyway.
        # Hardcoding the value is good enough.
        expire_after=timedelta(hours=12.0),
    )
    if settings.use_http_cache
    else requests.Session()
)


def get_json_data(url: str, **kwargs):
    http = session.get(url, **kwargs)
    status = http.status_code

    if status >= 300:
        raise RuntimeError(f"Got unhandled response code={status} : {http.json()}")

    logger.debug(
        "Got successful HTTP response from {cached}{url}",
        cached="cached " if isinstance(http, CachedResponse) else "",
        url=http.url,
    )

    return http.json()
