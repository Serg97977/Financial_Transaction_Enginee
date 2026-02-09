"""
Hashing Utility Module
----------------------
Provides secure password storage mechanisms using SHA-256 and unique salts.
This follows security best practices to prevent Rainbow Table attacks.

Dependencies:
- hashlib: For cryptographic hashing functions.
- os: For generating cryptographically strong random numbers.
"""

import os
import hashlib


def hashing(user_password):
    """
    Creates a secure hash for a plain-text password using a random salt.

    Args:
        user_password (str): The plain-text password provided by the user.

    Returns:
        dict: A dictionary containing:
            - 'hash' (str): The hex-encoded SHA-256 result.
            - 'salt' (str): The unique 16-byte hex-encoded salt.
    """
    # Generate a unique 16-byte salt for every password to ensure
    # identical passwords have different hashes.
    salt = os.urandom(16).hex()

    # Concatenate salt with password and encode to bytes for hashing
    hash_password = hashlib.sha256((salt + user_password).encode()).hexdigest()

    # Note to dev: Always store BOTH the hash and the salt in your database
    # to verify the password during the login process later.
    return {
        'hash': hash_password,
        'salt': salt
    }

