"""
A simple interactive shell based on IPython that can be used for dev/debugging purposes
"""

from IPython import embed

from opa.core import *
from opa.http_methods import get_json_data
from opa.storage import storage
from opa.providers import FmpCloud

fmp = FmpCloud()
embed()
