"""
A simple interactive shell based on IPython that can be used for dev/debugging purposes
"""

from IPython import embed

from opa.storage import storage
from opa.providers import FmpCloud
from opa.http_methods import get_json_data
from opa.env import get_secret, is_running_in_docker
from opa.financial_data import StockValueType

fmp = FmpCloud()
embed()
