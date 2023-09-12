import json
import base64
from pathlib import Path

from opa.core.auth import Authenticator, CredentialsStorage
from opa.config import settings


class JsonCredentialsStorage(CredentialsStorage):
    def __init__(self) -> None:
        self.storage_path = Path(settings.secrets_dir) / "credentials.json"

    def read_hashed_password(self, username: str) -> bytes | None:
        return self._read_credentials_file().get(username)

    def write(self, username: str, hashed_password: bytes):
        credentials = self._read_credentials_file()
        credentials[username] = hashed_password
        self._write_credentials_file(credentials)

    def remove(self, username: str):
        credentials = self._read_credentials_file()
        del credentials[username]
        self._write_credentials_file(credentials)

    def _read_credentials_file(self) -> dict:
        try:
            with open(self.storage_path) as f:
                return {
                    username: base64.b64decode(hash.encode("ascii"))
                    for username, hash in json.load(f).items()
                }
        except FileNotFoundError:
            return {}

    def _write_credentials_file(self, credentials: dict) -> None:
        str_credentials = {
            username: base64.b64encode(c).decode("ascii")
            for username, c in credentials.items()
        }

        with open(self.storage_path, "w") as f:
            json.dump(str_credentials, f, indent=4)


opa_auth = Authenticator(JsonCredentialsStorage())
