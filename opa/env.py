import os
from opa.core import Env


environment = Env(use_http_cache=bool(os.getenv("USE_HTTP_CACHE", False)))
