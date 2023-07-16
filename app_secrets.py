from pathlib import Path

from utils import is_running_in_docker


def get_base() -> Path:
    if is_running_in_docker():
        return Path("/run/secrets")
    else:
        path = Path("./secrets")
        if path.is_dir():
            return path
        else:
            raise EnvironmentError(
                f"Secrets should either be handled via Docker Secrets or stored in a {path} directory"
            )


base = get_base()


def get_secret(key: str) -> str:
    with open(base / key, "r") as f:
        return f.read()
