import logging
import bcrypt

logger = logging.getLogger(__name__)

def hash_password(plain_password: str) -> str:
    """Hashes a raw password string using bcrypt with error handling."""
    if not plain_password:
        raise ValueError("Password string cannot be empty.")
    
    try:
        password_bytes = plain_password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        return hashed_bytes.decode('utf-8')
    except Exception as e:
        logger.exception("Error hashing password")
        raise RuntimeError("Password security processing failed.") from e

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against a stored bcrypt hash string."""
    if not plain_password or not hashed_password:
        return False
    
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        # Fails safely if hash format is invalid
        return False