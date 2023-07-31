import requests

from loguru import logger
import requests_cache
from requests_cache.models.response import CachedResponse
from requests_cache.backends.sqlite import SQLiteCache

from opa import environment


session = (
    requests_cache.CachedSession(
        "opa", backend=SQLiteCache(db_path=environment.http_cache_db_dir / "opa")
    )
    if environment.use_http_cache
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
