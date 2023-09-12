from abc import ABC, abstractmethod
import secrets
from hashlib import scrypt
from loguru import logger


def encrypt_pass(password: bytes):
    return scrypt(password, n=2**14, r=8, p=1, salt=b"salt")


class Authenticator(ABC):
    @abstractmethod
    def read_hashed_password(self, username: str) -> bytes | None:
        ...

    @abstractmethod
    def write_credentials(self, username: str, password: bytes):
        ...

    @abstractmethod
    def remove_credentials(self, username: str):
        ...

    def add_user(self, username: str, password: str) -> bool:
        if self.read_hashed_password(username):
            logger.error("User {} already exists", username)
            return False
        else:
            self.write_credentials(username, encrypt_pass(password.encode()))
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
