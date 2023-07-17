import os
import requests
import requests_cache


session = (
    requests_cache.CachedSession("opa")
    if os.getenv("USE_HTTP_CACHE", False)
    else requests.Session()
)


def get_json_data(url: str, **kwargs):
    http = session.get(url, **kwargs)
    return http.json()
