import os
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Env:
    use_http_cache: bool
    secrets_dir: Path = field(init=False)
    http_cache_db_dir: Path = field(init=False)
    mongodb_host: str = field(init=False)
    mongodb_uri: str = field(init=False)

    def __post_init__(self):
        if self.is_running_in_docker():
            self.secrets_dir = Path("/run/secrets")
            self.http_cache_db_dir = Path("/var/http_cache")
            self.mongodb_host = "database"

        else:
            local_app_data = Path.cwd() / "app_data"
            self.secrets_dir = local_app_data / "secrets"
            self.http_cache_db_dir = local_app_data / "http_cache"
            self.mongodb_host = "localhost"

        self.mongodb_uri = "mongodb://{username}:{password}@{host}".format(
            username=self.get_secret("mongodb_username"),
            password=self.get_secret("mongodb_password"),
            host=self.mongodb_host,
        )

    def get_secret(self, key: str) -> str:
        with open(self.secrets_dir / key, "r") as f:
            # The "secret" is just the first line in the file, stripped of whitespace/end-of-line characters
            return f.readline().strip()

    @staticmethod
    def is_running_in_docker() -> bool:
        # Shamelessly copied/pasted from: https://stackoverflow.com/a/73564246
        cgroup = Path("/proc/self/cgroup")
        return (
            Path("/.dockerenv").is_file()
            or cgroup.is_file()
            and "docker" in cgroup.read_text()
        )


environment = Env(use_http_cache=bool(os.getenv("USE_HTTP_CACHE", False)))
