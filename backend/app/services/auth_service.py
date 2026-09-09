"""Authentication and password hashing utilities using PBKDF2-HMAC-SHA256."""
import hashlib
import secrets

ITERATIONS = 100_000


def hash_password(password: str) -> str:
    """Securely hash a plaintext password with a unique random salt."""
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        ITERATIONS,
    )
    return f"{salt}${dk.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a salt$hash string using constant-time comparison."""
    if not hashed_password or "$" not in hashed_password:
        return False
    try:
        salt, key = hashed_password.split("$", 1)
        new_dk = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            ITERATIONS,
        )
        return secrets.compare_digest(new_dk.hex(), key)
    except Exception:
        return False
