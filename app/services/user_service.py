"""
User Service Module
-------------------
Handles core database interactions for user onboarding and authentication.
Integrates user profiles, financial data, and security credentials across
the 'Financial_Transaction_Engine_System' database schema.

Functions:
- save: Persists new user records across multiple relational tables.
- checking_data: Validates login credentials using salt-hash comparisons.
"""

import hashlib
from app.config import mydb
from app.services.possible_errors import LoginEmailError, PasswordError


def save(data):
    """
    Performs a multi-table insertion for a new user account.

    Args:
        data (dict): Contains user profile, finance, and hashed security data.

    Returns:
        str: Success message or error notification.
    """
    try:
        mycursor = mydb.cursor()
        mycursor.execute("USE Financial_Transaction_Engine_System")

        # 1. Insert Core Profile Data
        query_users = (
            "INSERT INTO users (name, surname, birth_date, email, phone)"
            "VALUES(%s, %s, %s, %s, %s)"
        )

        mycursor.execute(query_users, (data['name'],
                                       data['surname'],
                                       data['birth_date'],
                                       data['email'],
                                       data['phone']
                                       ))

        # Retrieve the generated ID to link other tables
        user_id = mycursor.lastrowid

        # 2. Initialize Financial Record
        query_finances = "INSERT INTO finances (user_id, card_number) VALUES (%s, %s)"
        mycursor.execute(query_finances, (user_id, data['card_number']))

        # 3. Store Security Credentials (Salt & Hash)
        query_security = (
            "INSERT INTO security(user_id, salt, hash_password)"
            "VALUES(%s, %s, %s)"
        )

        mycursor.execute(query_security, (user_id,
                                          data['hash_password']['salt'],
                                          data['hash_password']['hash']))

    except TypeError:
        # Rollback ensures no partial data is saved if an error occurs
        mydb.rollback()
        return 'ERROR.'

    mydb.commit()
    mycursor.close()
    return 'Data Successfully Added !'


def checking_data(input_email, input_password):
    """
    Verifies user credentials by reconstructing the hash from stored salt.

    Args:
        input_email (str): Email provided during login.
        input_password (str): Plain-text password provided during login.

    Returns:
        list: [True, {identity_info}] on success.
        str: Error message on failure.
    """
    try:
        # Basic validation for empty inputs
        if not input_email.strip():
            raise LoginEmailError
        if not input_password.strip():
            raise PasswordError

        mycursor1 = mydb.cursor()
        mycursor1.execute("USE Financial_Transaction_Engine_System")

        # Fetch ID based on Email
        query_id = "SELECT id FROM users WHERE email = %s;"
        mycursor1.execute(query_id, (input_email,))
        user_result = mycursor1.fetchone()
        mycursor1.close()

        if user_result is None:
            raise LoginEmailError

        user_id = user_result[0]

        # Fetch Salt and Hash for verification
        mycursor2 = mydb.cursor()
        salt_hash_query = "SELECT salt, hash_password FROM security WHERE user_id = %s;"
        mycursor2.execute(salt_hash_query, (user_id,))
        salt_hash_result = mycursor2.fetchone()
        mycursor2.close()

        # Fetch Role for JWT/Session management
        mycursor3 = mydb.cursor()
        role_query = "SELECT role FROM users WHERE id = %s;"
        mycursor3.execute(role_query, (user_id,))
        user_role = mycursor3.fetchone()
        mycursor3.close()

        checking_answer = [True, {"user_id": user_id, "role": user_role}]

        if salt_hash_result is None:
            print(f"Error: No security data found for user ID {user_id}")
            mydb.rollback()
            raise LoginEmailError

        db_salt = salt_hash_result[0]
        db_hash = salt_hash_result[1]

        # Verify password: Hash(Salt + Input) == StoredHash
        input_hash_psw = hashlib.sha256((db_salt + input_password).encode()).hexdigest()

        if input_hash_psw == db_hash:
            return checking_answer
        else:
            raise PasswordError

    # Note to dev: Unified error messages prevent attackers from
    # identifying whether the email or password was the incorrect field.
    except (LoginEmailError, PasswordError, TypeError):
        return "Wrong password or email"
