import secrets
import json
import base64
from hashlib import scrypt


def encrypt_pass(password):
    c = scrypt(password, n=2, r=3, p=5, salt=b"salt")
    return base64.b64encode(c).decode("ascii")


creds_file = "app_data/secrets/creds.json"


def read_creds():
    with open(creds_file) as f:
        return json.load(f)


def auth_user(username, password):
    all_users = {"bob": encrypt_pass(b"pouet")}
    with open(creds_file, "w") as f:
        json.dump(all_users, f)

    expected_password = all_users.get(username)
    if expected_password:
        if secrets.compare_digest(expected_password, encrypt_pass(password.encode())):
            return True

    print("Bad credentials")
    return False
