import requests
import requests_cache


http_session = requests.Session()
http_cache_session = requests_cache.CachedSession("opa")


def get_json_data(url: str, use_cache=True, **kwargs):
    session = http_cache_session if use_cache else http_session
    http = session.get(url, **kwargs)
    return http.json()
