"""
A simple interactive shell based on IPython that can be used for dev/debugging purposes
"""

from IPython import embed

from opa.storage import storage
from opa.providers import FmpCloud
from opa.http_methods import get_json_data
from opa.app_secrets import get_secret
from opa.utils import is_running_in_docker

fmp = FmpCloud()
embed()
