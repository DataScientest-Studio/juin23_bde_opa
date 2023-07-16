from pathlib import Path


base = Path("/run/secrets")


def get_secret(key: str) -> str:
    with open(base / key, "r") as f:
        return f.read()
