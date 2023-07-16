from pathlib import Path


def get_base() -> Path:
    docker_path = Path("/run/secrets")
    local_path = Path("./secrets")

    if docker_path.is_dir():
        return docker_path
    elif local_path.is_dir():
        return local_path
    else:
        raise EnvironmentError(
            f"There should be a {docker_path} or a {local_path} dir for secrets"
        )


base = get_base()


def get_secret(key: str) -> str:
    with open(base / key, "r") as f:
        return f.read()
