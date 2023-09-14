from abc import ABC, abstractmethod
from loguru import logger
from dataclasses import dataclass, field

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class CredentialsStorage(ABC):
    @abstractmethod
    def read_hashed_password(self, username: str) -> str | None:
        ...

    @abstractmethod
    def write(self, username: str, password: str):
        ...

    @abstractmethod
    def remove(self, username: str):
        ...


@dataclass
class Authenticator:
    credentials_storage: CredentialsStorage
    hasher: PasswordHasher = field(default_factory=PasswordHasher)

    def add_user(self, username: str, password: str) -> bool:
        if self.credentials_storage.read_hashed_password(username):
            logger.error("User {} already exists", username)
            return False
        else:
            hashed = self.hasher.hash(password)
            self.credentials_storage.write(username, hashed)
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
            try:
                self.hasher.verify(expected_password, password)
                return True
            except VerifyMismatchError:
                return False
