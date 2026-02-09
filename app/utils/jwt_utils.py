"""
JWT Utility Module
------------------
Handles the generation and validation of JSON Web Tokens (JWT) for
user authentication and role-based access control.

Dependencies:
- PyJWT: For encoding and decoding tokens.
- python-dotenv: For managing the SECRET_KEY in environment variables.
"""

import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jwt import ExpiredSignatureError

# Load environment variables from .env file
load_dotenv()
SECRET_KEY = os.getenv("JWT_KEY")
ALGORITHM = 'HS256'


def create_jwt(user_id: int, role: str):
    """
    Generates a new JWT for a specific user.

    Args:
        user_id (int): Unique identifier of the user.
        role (str): User permissions level (e.g., 'admin' or 'user').

    Returns:
        str: Encoded JWT string or error message.
    """
    try:
        # Token validity period (Set to 1 hour)
        expiration_time = datetime.utcnow() + timedelta(hours=1)

        payload = {
            'user_id': user_id,
            'role': role,
            'exp': expiration_time  # Registered claim: Expiration Time
        }

        # Sign the payload with the Secret Key
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
    except ExpiredSignatureError:
        # Note to dev: ExpiredSignatureError usually occurs during decoding,
        # but kept here for safety in case of clock-skew issues during creation.
        return 'Try again.'


def decode_jwt(token: str):
    """
    Deciphers an encoded JWT to retrieve user identity and claims.

    Args:
        token (str): The JWT string provided by the client.

    Returns:
        dict: The original payload (user_id, role, etc.) if valid.

    Raises:
        jwt.exceptions.DecodeError: If the signature is invalid.
        jwt.exceptions.ExpiredSignatureError: If the current time is past 'exp'.
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    return payload

