from pathlib import Path

from opa.utils import is_running_in_docker


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
        # The "secret" is just the first line in the file, stripped of whitespace/end-of-line characters
        return f.readline().strip()
