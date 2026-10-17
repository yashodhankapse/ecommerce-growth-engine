import hashlib
import hmac
import secrets

from backend.database import get_connection


def hash_password(password):
    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200_000
    ).hex()

    return f"{salt}${password_hash}"


def verify_password(password, stored_hash):
    try:
        salt, expected_hash = stored_hash.split("$", 1)

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            200_000
        ).hex()

        return hmac.compare_digest(
            actual_hash,
            expected_hash
        )

    except (ValueError, AttributeError):
        return False


def register_user(name, email, password):
    name = name.strip()
    email = email.strip().lower()

    if not name or not email or not password:
        return False, "All fields are required."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO users
                (name, email, password_hash, role)
                VALUES (?, ?, ?, 'user')
                """,
                (name, email, hash_password(password))
            )

        return True, "Account created successfully."

    except Exception as exc:
        if "UNIQUE constraint failed" in str(exc):
            return False, "Email is already registered."

        return False, "Could not create account."


def authenticate_user(email, password):
    email = email.strip().lower()

    with get_connection() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

    if user and verify_password(
        password,
        user["password_hash"]
    ):
        return {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }

    return None