import secrets
import json
import base64
from hashlib import scrypt
from loguru import logger


def encrypt_pass(password: bytes):
    return scrypt(password, n=2**14, r=8, p=1, salt=b"salt")


class Authenticator:
    creds_file = "app_data/secrets/creds.json"

    def read_hashed_password(self, username: str) -> bytes | None:
        return self._read_credentials_file().get(username)

    def write_credentials(self, username: str, password: str):
        credentials = self._read_credentials_file()
        credentials[username] = encrypt_pass(password.encode())
        self._write_credentials_file(credentials)

    def remove_credentials(self, username: str):
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

    def add_user(self, username: str, password: str) -> bool:
        if self.read_hashed_password(username):
            logger.error("User {} already exists", username)
            return False
        else:
            self.write_credentials(username, password)
            logger.info("User {} successfully added", username)
            return True

    def remove_user(self, username: str):
        self.remove_credentials(username)

    def auth_user(self, username, password):
        expected_password = self.read_hashed_password(username)
        if expected_password is None:
            return False
        else:
            return secrets.compare_digest(
                expected_password, encrypt_pass(password.encode())
            )


auth = Authenticator()
