"""
User Functions Module
---------------------
Provides core features for the logged-in user session.
This includes balance checking, profile viewing, transaction history retrieval,
and account detail updates (phone, email, password).

Security:
- All functions utilize JWT (JSON Web Tokens) to verify user identity.
- Role-based checks prevent administrative access to user-specific data.
"""

import re
import phonenumbers
from app.utils.hashing import hashing
from phonenumbers.phonenumberutil import NumberParseException
from app.config import mydb
from app.utils.jwt_utils import decode_jwt
from app.services.auth_service import user_jwt
from app.services.possible_errors import UserError, PhoneNumberError, EmailError
from jwt import ExpiredSignatureError


def show_balance():
    """Fetches the current account balance for the authenticated user."""
    try:
        decoded_jwt = decode_jwt(user_jwt[0])
        user_id = decoded_jwt['user_id']
        user_role = decoded_jwt['role']

        # Guard clause: Ensure admins cannot access user balance logic here
        if user_role == ('admin',):
            raise UserError
        elif not str(user_id).strip():
            raise UserError
        else:
            mycursor = mydb.cursor()
            mycursor.execute("USE Financial_Transaction_Engine_System")

            balance_query = "SELECT balance FROM finances WHERE user_id = %s"
            mycursor.execute(balance_query, (user_id,))

            user_balance = mycursor.fetchone()[0]
            mycursor.close()
            return f"Your balance: {user_balance}"

    except UserError:
        return "Something went wrong."
    except ExpiredSignatureError:
        return "Try again."


def show_transaction_history():
    """Retrieves the transaction logs associated with the user's ID."""
    try:
        decoded_jwt = decode_jwt(user_jwt[0])
        user_id = decoded_jwt['user_id']
        user_role = decoded_jwt['role']

        if user_role == ('admin',) or user_id == None:
            raise UserError
        else:
            mycursor = mydb.cursor()
            mycursor.execute("USE Financial_Transaction_Engine_System")

            transaction_history_query = "SELECT FromCard, ToCard, amount, date FROM history WHERE user_id = %s"
            mycursor.execute(transaction_history_query, (user_id,))

            transaction_history = mycursor.fetchall()
            if not transaction_history:
                raise UserError
            else:
                mycursor.close()

            # Note to dev: Fetches only the first entry; logic for multiple entries needed
            return (f"From your card :{transaction_history[0][0]}\n"
                    f"To card: {transaction_history[0][1]} \n"
                    f"Amount: {transaction_history[0][2]} \n"
                    f"Date: {transaction_history[0][3]} ")

    except UserError:
        return "Something went wrong."
    except ExpiredSignatureError:
        return "Try again."


def show_profile():
    """Returns basic user profile information from the database."""
    try:
        decoded_jwt = decode_jwt(user_jwt[0])
        user_id = decoded_jwt['user_id']
        user_role = decoded_jwt['role']

        if user_role == ('admin',) or user_id == None:
            raise UserError
        else:
            mycursor = mydb.cursor()
            mycursor.execute("USE Financial_Transaction_Engine_System")

            show_profile_query = "SELECT name, surname, email, phone FROM users WHERE id = %s"
            mycursor.execute(show_profile_query, (user_id,))

            user_profile = mycursor.fetchall()
            mycursor.close()
            return (f"Your name : {user_profile[0][0]}\n"
                    f"Your Surname : {user_profile[0][1]}\n"
                    f"Your E-mail : {user_profile[0][2]}\n"
                    f"Your phone number : {user_profile[0][3]}")

    except UserError:
        return "Something went wrong."
    except ExpiredSignatureError:
        return "Try again."


def change_number(input_number: int) -> str:
    """Updates the user's phone number after validation."""
    try:
        decoded_jwt = decode_jwt(user_jwt[0])
        user_id = decoded_jwt['user_id']
        user_role = decoded_jwt['role']

        if user_role == ('admin',) or user_id == None:
            raise UserError

        # Validate international phone number format
        number = phonenumbers.parse(input_number)
        is_valid = phonenumbers.is_valid_number(number)
        if is_valid == False:
            raise PhoneNumberError
        else:
            mycursor = mydb.cursor()
            mycursor.execute("USE Financial_Transaction_Engine_System")

            change_name_query = "UPDATE users SET phone = %s WHERE id = %s;"
            mycursor.execute(change_name_query, (input_number, user_id))

            mydb.commit()
            mycursor.close()
            return "Your phone number has been successfully changed."

    except ExpiredSignatureError:
        return "Try again."
    except NumberParseException:
        return "Wrong number."


def change_email(input_email: str) -> str:
    """Updates user email after verifying structure via Regex."""
    try:
        if not input_email.strip():
            raise EmailError

        # Regex for standard email validation
        x = bool(re.search(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$', input_email))
        if x == False:
            raise EmailError

        decoded_jwt = decode_jwt(user_jwt[0])
        user_id = decoded_jwt['user_id']
        user_role = decoded_jwt['role']

        if user_role == ('admin',) or user_id == None:
            raise UserError
        else:
            mycursor = mydb.cursor()
            mycursor.execute("USE Financial_Transaction_Engine_System")

            change_email_query = "UPDATE users SET email = %s WHERE id = %s;"
            mycursor.execute(change_email_query, (input_email, user_id))

            mydb.commit()
            mycursor.close()
            return "Your email has been successfully changed."

    except ExpiredSignatureError:
        return "Try again."
    except UserError:
        return "Something wnet wrong."
    except EmailError:
        return "Wrong e-mail."


def change_password() -> str:
    """
    Prompt user for a new password and perform complexity checks.
    Once valid, hashes the password and updates the security table.
    """
    try:
        while True:
            user_psw = input("Enter your new password: ")

            upper_counter = 0
            digit_counter = 0

            # Logic check: Requirement for at least one uppercase and one digit
            for i in user_psw:
                if i.isupper():
                    upper_counter += 1
                elif i.isdigit():
                    digit_counter += 1

            if not user_psw.strip():
                print("Password cannot be empty.")
            elif len(user_psw) < 6:
                print("Password must, be at least 6 characters long.")
            elif upper_counter == 0:
                print('Password has to contain at least 1 character of UpperCase.(A-Z)')
            elif digit_counter == 0:
                print("Password has to contain at least 1 digit.(0-9) ")
            else:
                # Generate new Salt and Hash via the hashing utility
                hashed_password = hashing(user_psw)

                decoded_jwt = decode_jwt(user_jwt[0])
                user_id = decoded_jwt['user_id']
                user_role = decoded_jwt['role']

                if user_role == ('admin',) or user_id == None:
                    raise UserError

                mycursor = mydb.cursor()
                mycursor.execute("USE Financial_Transaction_Engine_System")

                # Update the salt and hash—original password is never stored
                change_security_param_query = "UPDATE security SET salt = %s, hash_password = %s WHERE user_id = %s;"
                mycursor.execute(change_security_param_query,
                                 (hashed_password["salt"], hashed_password["hash"], user_id))

                mydb.commit()  # Note to dev: Ensure commit is called to persist password change
                return "Your password has been successfully changed. "

    except ExpiredSignatureError:
        return "Try again."
    except UserError:
        return "Something wnet wrong."
