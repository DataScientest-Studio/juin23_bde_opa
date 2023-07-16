from pathlib import Path


def is_running_in_docker() -> bool:
    # Shamelessly copied/pasted from: https://stackoverflow.com/a/73564246
    cgroup = Path("/proc/self/cgroup")
    return (
        Path("/.dockerenv").is_file()
        or cgroup.is_file()
        and "docker" in cgroup.read_text()
    )
