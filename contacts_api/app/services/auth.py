# services/auth.py
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from pydantic import EmailStr

# Налаштування для токену
SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
EXPIRE_MINUTES = 60 * 24


def create_email_token(data: dict) -> str:
    """
        Create a JWT token for email verification.

        :param data: dict: Data to include in the token (e.g., {"sub": email}).
        :return: str: Encoded JWT token.
        """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_email_token(token: str):
    """
        Verify a JWT email token and extract the email.

        :param token: str: JWT token to verify.
        :return: EmailStr: Email address extracted from the token.
        :raises HTTPException: If the token is invalid or expired.
        """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload["sub"]
        return email
    except jwt.PyJWTError:
        raise HTTPException(status_code=422, detail="Invalid token")
