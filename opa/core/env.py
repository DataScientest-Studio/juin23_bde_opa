from pathlib import Path


def is_running_in_docker() -> bool:
    # Shamelessly copied/pasted from: https://stackoverflow.com/a/73564246
    cgroup = Path("/proc/self/cgroup")
    return (
        Path("/.dockerenv").is_file()
        or cgroup.is_file()
        and "docker" in cgroup.read_text()
    )


def _get_base() -> Path:
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


base = _get_base()


def get_secret(key: str) -> str:
    with open(base / key, "r") as f:
        # The "secret" is just the first line in the file, stripped of whitespace/end-of-line characters
        return f.readline().strip()
