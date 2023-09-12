import secrets
import json
import base64
from hashlib import scrypt
from loguru import logger


creds_file = "app_data/secrets/creds.json"


def encrypt_pass(password: bytes):
    return scrypt(password, n=2**14, r=8, p=1, salt=b"salt")


def read_credentials() -> dict:
    with open(creds_file) as f:
        return {
            username: base64.b64decode(hash.encode("ascii"))
            for username, hash in json.load(f).items()
        }


def write_credentials(credentials: dict) -> None:
    str_credentials = {
        username: base64.b64encode(c).decode("ascii")
        for username, c in credentials.items()
    }

    with open(creds_file, "w") as f:
        json.dump(str_credentials, f, indent=4)


def add_user(username: str, password: str) -> bool:
    credentials = read_credentials()
    if credentials.get(username):
        logger.error("User {} already exists", username)
        return False
    else:
        credentials[username] = encrypt_pass(password.encode())
        write_credentials(credentials)
        logger.info("User {} successfully added", username)
        return True


def remove_user(username: str):
    credentials = read_credentials()
    del credentials[username]
    write_credentials(credentials)


def auth_user(username, password):
    credentials = read_credentials()

    expected_password = credentials.get(username)
    if expected_password is None:
        return False
    else:
        return secrets.compare_digest(
            expected_password, encrypt_pass(password.encode())
        )
