"""
A simple interactive shell based on IPython that can be used for dev/debugging purposes
"""

from IPython import embed

from opa.core import *
from opa.http_methods import get_json_data
from opa.providers import opa_provider
from opa.storage import opa_storage

embed()
