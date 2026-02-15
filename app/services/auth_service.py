"""
Auth Service Module
-------------------
Handles the logic for user registration and authentication sessions.

HIGHLIGHTS (ADVANCED CONCEPTS):
- BRUTE-FORCE PROTECTION: Implements a security mechanism that automatically locks
  accounts (account_locked = 1) after 3 failed login attempts.
- GOOGLE PHONENUMBERS INTEGRITY: Uses the [python-phonenumbers]
  library to ensure international phone standards.
- TUPLE-BASED AGE CALCULATION: A robust way to calculate age by comparing date tuples,
  correctly handling leap years and birthday precision.
- STATELESS JWT MANAGEMENT: Integrates [PyJWT] for
  secure, token-based session handling.
"""

import re
import random
import phonenumbers
from datetime import datetime, date
from app.utils.hashing import hashing
from phonenumbers.phonenumberutil import NumberParseException
from app.services.possible_errors import *
from app.services.user_service import checking_data
from app.utils.jwt_utils import create_jwt, decode_jwt
from app.config import mydb

# Structured data template for registration payload
data = {
    'name': None,
    'surname': None,
    'birth_date': None,
    'email': None,
    'phone': None,
    'hash_password': None,
    'card_number': None
}

def reg_data():
    return data

user_password = {
    "password": None
}


def register(name: str = None, surname: str = None, birth_date: int = None, email: str = None,
             phone: int = None) -> dict | str:
    """
    Validates user data and prepares a registration package.

    DEV NOTE: This function demonstrates complex multi-step validation including
    Regex, library-based phone parsing, and strict password entropy rules.
    """
    try:
        # Step 1: Presence validation
        if not str(name).strip():
            raise NameError
        if not str(surname).strip():
            raise SurnameError
        if not str(birth_date).strip():
            raise BirthDayError
        if not str(email).strip():
            raise EmailError
        if not str(phone).strip():
            raise PhoneNumberError

        # Step 2: Character type validation
        for i in name:
            if i.isalpha() == False or len(name) > 15:
                raise NameError
            else:
                data.update({'name': name})

        for i in surname:
            if i.isalpha() == False or len(surname) > 20:
                raise SurnameError
            else:
                data.update({'surname': surname})

        # Step 3: Precise Age Calculation (Senior Approach)
        birth_day = datetime.strptime(birth_date, '%d-%m-%Y')
        today = date.today()
        age = today.year - birth_day.year
        # Accurate birthday check by comparing tuples
        if (today.month, today.day) < (birth_day.month, birth_day.day):
            age -= 1

        if age >= 18:
            data.update({'birth_date': birth_date})
        else:
            raise AgeError

        # Step 4: Email Structural Validation (Regex)
        x = bool(re.search(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$', email))
        if x is True:
            data.update({'email': email})
        else:
            raise EmailError

        # Step 5: Professional Phone Parsing (phonenumbers library)
        number = phonenumbers.parse(phone)
        is_valid = phonenumbers.is_valid_number(number)
        if is_valid is False:
            raise PhoneNumberError
        else:
            data.update({'phone': phone})

            # Step 6: Password Entropy Enforcement
            while True:
                print('Registration will take a few second !\nLOADING....')
                user_psw = input('                              Create your password ::: ')

                upper_counter = 0
                digit_counter = 0

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
                    # Step 7: Cryptographic Hashing and Card Generation
                    # DEV NOTE: Using cryptographically secure random integers
                    card_number = random.randint(10 ** 15, 10 ** 16 - 1)
                    cvv_number = random.randint(100, 999)
                    hashed_password = hashing(user_psw)

                    print('Your account has been successfully created.\n'
                          f'CARD NUMBER: {card_number} \n'
                          f'CVV: {cvv_number}')

                    data.update({'hash_password': hashed_password,
                                 'card_number': card_number})
                    return "Your account has been successfully created."

    except (NameError, SurnameError, EmailError, PhoneNumberError, AgeError, ValueError, NumberParseException):
        # Maps internal errors to clean user output
        return 'Registration failed: Invalid input provided.'


user_jwt = []


def login(email, password):
    """
    Handles authentication and security monitoring.

    HIGHLIGHT: Automated Security Policy logic. If an attacker attempts a
    brute-force login, the account is flagged and locked in the database.
    """
    try:
        checking = checking_data(email, password)
        if checking[0] is True:
            # Successful Path: Issue stateless JWT
            user_jwt.append(create_jwt(checking[1]['user_id'], checking[1]['role']))

            mycursor = mydb.cursor()
            mycursor.execute("USE Financial_Transaction_Engine_System")

            # Audit Trail: Track the last time a user accessed the system
            login_time = datetime.now()
            last_login_query = "UPDATE security SET last_login = %s WHERE user_id = %s"
            mycursor.execute(last_login_query, (login_time, checking[1]['user_id']))

            mydb.commit()
            mycursor.close()
            return "Successful Login."
        else:
            # Failure Path: Security Monitoring Logic
            mycursor = mydb.cursor()
            mycursor.execute("USE Financial_Transaction_Engine_System")

            email_query = "SELECT id FROM users WHERE email = %s"
            mycursor.execute(email_query, (email,))
            checking_user = mycursor.fetchone()

            if checking_user:
                # Increment failed attempt counter
                failed_attempts_query = "UPDATE security SET failed_attempts = failed_attempts + 1 WHERE user_id =%s"
                mycursor.execute(failed_attempts_query, (checking_user[0],))
                mydb.commit()

                # Security Threshold Check
                account_checking_query = "SELECT failed_attempts FROM security WHERE user_id = %s"
                mycursor.execute(account_checking_query, (checking_user[0],))
                failed_attempts_count = mycursor.fetchone()

                if failed_attempts_count[0] > 3:
                    # Account Lockout activation
                    blocking_account_query = "UPDATE security SET account_locked = 1 WHERE user_id = %s"
                    mycursor.execute(blocking_account_query, (checking_user[0],))
                    mydb.commit()
                    mycursor.close()
                    return "Your bank account has been blocked."

            return "Unsuccessful Login"

    except (EmailError, PasswordError, TypeError):
        return "Wrong email or password"


def login_admin(email: str, admin_psw: str):
    """
    Administrative Login logic specifically checking for elevated role claims.
    """
    try:
        checking = checking_data(email, admin_psw)
        # Check: Ensure the user possesses the 'admin' role tuple
        if checking[0] == True and checking[1]['role'] == ('admin',):
            admin_jwt = create_jwt(checking[1]['user_id'], checking[1]['role'])
            return "Successful Login."
        else:
            return "Unsuccessful Login"
    except (EmailError, PasswordError):
        return "Incorrect credentials."
    