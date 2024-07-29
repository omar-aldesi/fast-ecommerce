import os
import re
from passlib.context import CryptContext
from dotenv import load_dotenv
from app.core.log import logger

# Load environment variables
load_dotenv()

# Create a password context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=int(os.getenv("BCRYPT_ROUNDS", 12))  # Configurable work factor
)


def hash_password(password: str) -> str:
    """
    Hash a password for storing.
    """
    return pwd_context.hash(password)


def verify_password(hashed_password: str, plain_password: str) -> bool:
    """
    Verify a stored password against one provided by user
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.warning(f"Password verification failed: {str(e)}")
        return False


def validate_password(password: str) -> bool:
    """
    Validate the password against the following criteria:
    1. At least 8 characters long
    2. Contains at least one uppercase letter
    3. Contains at least one lowercase letter
    4. Contains at least one digit
    5. Contains at least one special character
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")

    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain at least one uppercase letter")

    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain at least one lowercase letter")

    if not re.search(r'\d', password):
        raise ValueError("Password must contain at least one digit")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValueError("Password must contain at least one special character")
    return True
