import os
from pathlib import Path

from dynaconf import Dynaconf


def get_secret(file: str) -> str:
    with open(file, "r") as f:
        # The "secret" is just the first line in the file, stripped of whitespace/end-of-line characters
        return f.readline().strip()


def load_secrets(settings):
    root = Path(settings.secrets_dir)

    data = {"dynaconf_merge": True}
    try:
        data["secrets"] = {
            file: get_secret(root / file)
            for file in os.listdir(root)
            if not file.startswith(".")
        }
    except FileNotFoundError:
        ...

    return data


settings = Dynaconf(
    environments=True,
    envvar_prefix="OPA",
    settings_files=["settings.toml"],
    post_hooks=load_secrets,
)
