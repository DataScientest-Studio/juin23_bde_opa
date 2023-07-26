import os
from pathlib import Path
import requests

import requests_cache
from requests_cache.backends import SQLiteCache

from opa.core.env import is_running_in_docker


http_cache_db_dir = (
    Path("/var/http_cache")
    if is_running_in_docker()
    else Path.cwd() / "app_data" / "http_cache"
)
session = (
    requests_cache.CachedSession(
        "opa", backend=SQLiteCache(db_path=http_cache_db_dir / "opa")
    )
    if os.getenv("USE_HTTP_CACHE", False)
    else requests.Session()
)


def get_json_data(url: str, **kwargs):
    http = session.get(url, **kwargs)
    status = http.status_code

    if status >= 300:
        raise RuntimeError(f"Got unhandled response code={status} : {http.json()}")

    return http.json()
