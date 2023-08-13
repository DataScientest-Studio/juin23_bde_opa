import os
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Env:
    use_http_cache: bool
    secrets_dir: Path = field(init=False)
    http_cache_db_dir: Path = field(init=False)

    def __post_init__(self):
        local_app_data = Path("app_data")

        secrets_dir = os.getenv("SECRETS_DIR")
        self.secrets_dir = (
            Path(secrets_dir) if secrets_dir else local_app_data / "secrets"
        )

        http_cache_db_dir = os.getenv("HTTP_CACHE_DIR")
        self.http_cache_db_dir = (
            Path(http_cache_db_dir)
            if http_cache_db_dir
            else local_app_data / "http_cache"
        )

    def get_secret(self, key: str) -> str:
        with open(self.secrets_dir / key, "r") as f:
            # The "secret" is just the first line in the file, stripped of whitespace/end-of-line characters
            return f.readline().strip()
