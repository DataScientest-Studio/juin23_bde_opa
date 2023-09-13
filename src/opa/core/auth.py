from abc import ABC, abstractmethod
import secrets
from hashlib import scrypt
from loguru import logger
from dataclasses import dataclass


def encrypt_pass(password: bytes):
    return scrypt(password, n=2**14, r=8, p=1, salt=b"salt")


class CredentialsStorage(ABC):
    @abstractmethod
    def read_hashed_password(self, username: str) -> bytes | None:
        ...

    @abstractmethod
    def write(self, username: str, password: bytes):
        ...

    @abstractmethod
    def remove(self, username: str):
        ...


@dataclass
class Authenticator:
    credentials_storage: CredentialsStorage

    def add_user(self, username: str, password: str) -> bool:
        if self.credentials_storage.read_hashed_password(username):
            logger.error("User {} already exists", username)
            return False
        else:
            self.credentials_storage.write(username, encrypt_pass(password.encode()))
            logger.info("User {} successfully added", username)
            return True

    def remove_user(self, username: str) -> None:
        self.credentials_storage.remove(username)
        logger.info("User {} successfully removed", username)

    def auth_user(self, username, password) -> bool:
        expected_password = self.credentials_storage.read_hashed_password(username)
        if expected_password is None:
            return False
        else:
            return secrets.compare_digest(
                expected_password, encrypt_pass(password.encode())
            )
