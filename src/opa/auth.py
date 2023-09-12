import json
import base64

from opa.core.auth import Authenticator, CredentialsStorage


class JsonCredentialsStorage(CredentialsStorage):
    def __init__(self, file) -> None:
        self.creds_file = file

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
        with open(self.creds_file) as f:
            return {
                username: base64.b64decode(hash.encode("ascii"))
                for username, hash in json.load(f).items()
            }

    def _write_credentials_file(self, credentials: dict) -> None:
        str_credentials = {
            username: base64.b64encode(c).decode("ascii")
            for username, c in credentials.items()
        }

        with open(self.creds_file, "w") as f:
            json.dump(str_credentials, f, indent=4)


auth = Authenticator(JsonCredentialsStorage("app_data/secrets/creds.json"))
