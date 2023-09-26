"""
A simple interactive shell based on IPython that can be used for dev/debugging purposes
"""

from IPython import start_ipython
from traitlets.config import Config


c = Config()
c.InteractiveShellApp.extensions = ["autoreload"]
c.InteractiveShellApp.exec_lines = [
    'print("Welcome to OPA Shell")',
    "%autoreload 2",
    "from opa.core import *",
    "from opa.config import settings",
    "from opa.http_methods import get_json_data",
    "from opa.providers import opa_provider",
    "from opa.storage import opa_storage",
    "from opa.data_report import api",
]
c.InteractiveShell.confirm_exit = False
c.TerminalIPythonApp.display_banner = False

start_ipython(config=c)
