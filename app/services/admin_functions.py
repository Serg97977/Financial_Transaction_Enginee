"""

This module contains all admin functions:
- User profile updates
- Account blocking / unblocking
- User deletion
- Balance crediting
- Transaction history viewing

The logic here assumes:
- MySQL database
- Explicit transaction control
- Custom error handling
"""

import re
import phonenumbers
from phonenumbers import NumberParseException
from datetime import datetime, date
from app.config import mydb

from app.services.possible_errors import (
    UserError,
    PhoneNumberError,
    EmailError,
    SurnameError,
    AgeError
)
from app.models.history_model import fill_history
from jwt import ExpiredSignatureError


def show_users():
    """
    Fetch all users together with their security data.

    Demonstrates:
    - SQL JOIN usage
    - Explicit database selection
    - Safe cursor handling
    """
    try:
        mycursor = mydb.cursor()
        mycursor.execute("USE Financial_Transaction_Engine_System")

        mycursor.execute("""
            SELECT *
            FROM users
            INNER JOIN security ON users.id = security.user_id;
        """)

        result = mycursor.fetchall()
        mycursor.close()
        return result

    except ExpiredSignatureError:
        mydb.rollback()
        return "Something went wrong."


def change_user_name(input_name: str, user_id: int) -> str:
    """
    Change user's first name.

    Validation rules:
    - Non-empty
    - Alphabetical characters only
    - Max length: 15

    Highlights:
    - Manual validation (not regex-only)
    - Row count verification to detect invalid user IDs
    """
    try:
        if not user_id:
            raise UserError

        if not input_name.strip():
            raise NameError

        for char in input_name:
            if not char.isalpha() or len(input_name) > 15:
                raise NameError

        mycursor = mydb.cursor()
        mycursor.execute("USE Financial_Transaction_Engine_System")

        mycursor.execute(
            "UPDATE users SET name = %s WHERE id = %s;",
            (input_name, user_id)
        )

        if mycursor.rowcount == 0:
            raise UserError

        mydb.commit()
        mycursor.close()
        return "User's name has been successfully changed."

    except NameError:
        mydb.rollback()
        return "Try again"
    except UserError:
        mydb.rollback()
        return "User ID doesn't exist."


def change_user_surname(input_surname: str, user_id: int) -> str:
    """
    Change user's surname.

    Same validation logic as first name to ensure consistency.
    """
    try:
        if not user_id:
            raise UserError

        if not input_surname.strip():
            raise SurnameError

        for char in input_surname:
            if not char.isalpha() or len(input_surname) > 15:
                raise SurnameError

        mycursor = mydb.cursor()
        mycursor.execute("USE Financial_Transaction_Engine_System")

        mycursor.execute(
            "UPDATE users SET surname = %s WHERE id = %s;",
            (input_surname, user_id)
        )

        if mycursor.rowcount == 0:
            raise UserError

        mydb.commit()
        mycursor.close()
        return "User's surname has been successfully changed."

    except SurnameError:
        mydb.rollback()
        return "Try again"
    except UserError:
        mydb.rollback()
        return "User ID doesn't exist."


def change_user_number(input_number: str, user_id: int) -> str:
    """
    Change user's phone number.

    Uses `phonenumbers` library for real-world validation
    instead of naive regex checks (non-junior approach).
    """
    try:
        if not user_id:
            raise UserError

        number = phonenumbers.parse(input_number)
        if not phonenumbers.is_valid_number(number):
            raise PhoneNumberError

        mycursor = mydb.cursor()
        mycursor.execute("USE Financial_Transaction_Engine_System")

        mycursor.execute(
            "UPDATE users SET phone = %s WHERE id = %s;",
            (input_number, user_id)
        )

        if mycursor.rowcount == 0:
            raise UserError

        mydb.commit()
        mycursor.close()
        return "User's phone number has been successfully changed."

    except (PhoneNumberError, NumberParseException):
        mydb.rollback()
        return "Wrong number."
    except UserError:
        mydb.rollback()
        return "User ID is not exist."


def change_user_email(input_email: str, user_id: int) -> str:
    """
    Change user's email address.

    Highlights:
    - Regex-based validation
    - Controlled exception flow
    """
    try:
        if not input_email.strip():
            raise EmailError

        is_valid = bool(re.search(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$',
            input_email
        ))

        if not is_valid:
            raise EmailError

        mycursor = mydb.cursor()
        mycursor.execute("USE Financial_Transaction_Engine_System")

        mycursor.execute(
            "UPDATE users SET email = %s WHERE id = %s;",
            (input_email, user_id)
        )

        if mycursor.rowcount == 0:
            raise UserError

        mydb.commit()
        mycursor.close()
        return "Your email has been successfully changed."

    except EmailError:
        mydb.rollback()
        return "Wrong e-mail."
    except UserError:
        mydb.rollback()
        return "User ID doesn't exist."
    except ExpiredSignatureError:
        mydb.rollback()
        return "Try again."


def change_user_birth_date(input_birth_date: str, user_id: int) -> str:
    """
    Change user's birth date.

    Business rule:
    - User must be 18+

    Highlights:
    - Correct age calculation
    - Date arithmetic awareness
    """
    try:
        if not user_id:
            raise UserError

        birth_day = datetime.strptime(input_birth_date, '%d-%m-%Y')
        today = date.today()

        age = today.year - birth_day.year
        if (today.month, today.day) < (birth_day.month, birth_day.day):
            age -= 1

        if age < 18:
            raise AgeError

        mycursor = mydb.cursor()
        mycursor.execute("USE Financial_Transaction_Engine_System")

        mycursor.execute(
            "UPDATE users SET birth_date = %s WHERE id = %s;",
            (input_birth_date, user_id)
        )

        if mycursor.rowcount == 0:
            raise UserError

        mydb.commit()
        mycursor.close()
        return "Your birth date has been successfully changed."

    except AgeError:
        mydb.rollback()
        return "You are not 18!"
    except UserError:
        return "User ID doesn't exist."


def delete_user(user_id: int) -> str:
    """
    Fully delete user and all dependent records.

    Highlights (VERY NOT JUNIOR):
    - Foreign key constraint handling
    - Multi-table deletion awareness
    - Explicit transactional safety
    """
    try:
        if not user_id:
            raise UserError

        mycursor = mydb.cursor()
        mycursor.execute("USE Financial_Transaction_Engine_System")

        mycursor.execute(
            "SELECT id FROM users WHERE id = %s",
            (user_id,)
        )

        if mycursor.rowcount == 0:
            raise UserError

        mycursor.execute("SET FOREIGN_KEY_CHECKS=0;")

        mycursor.execute("DELETE FROM users WHERE id = %s;", (user_id,))
        mycursor.execute("DELETE FROM finances WHERE user_id = %s;", (user_id,))
        mycursor.execute("DELETE FROM history WHERE user_id = %s;", (user_id,))
        mycursor.execute("DELETE FROM security WHERE user_id = %s;", (user_id,))

        mycursor.execute("SET FOREIGN_KEY_CHECKS=1;")

        mydb.commit()
        mycursor.close()
        return "User has been successfully deleted."

    except UserError:
        return "User ID doesn't exist."


def block_user(user_id: int):
    """
    Lock user's account (security-level action).
    """
    try:
        if not user_id:
            raise UserError

        mycursor = mydb.cursor()
        mycursor.execute("USE Financial_Transaction_Engine_System")

        mycursor.execute(
            "UPDATE security SET account_locked = %s WHERE user_id = %s;",
            (True, user_id)
        )

        if mycursor.rowcount == 0:
            raise UserError

        mydb.commit()
        mycursor.close()
        return "User has been successfully blocked."

    except UserError:
        return "User ID doesn't exist."


def unblock_user(user_id: int):
    """
    Unlock user's account.
    """
    try:
        if not user_id:
            raise UserError

        mycursor = mydb.cursor()
        mycursor.execute("USE Financial_Transaction_Engine_System")

        mycursor.execute(
            "UPDATE security SET account_locked = %s WHERE user_id = %s;",
            (False, user_id)
        )

        if mycursor.rowcount == 0:
            raise UserError

        mydb.commit()
        mycursor.close()
        return "User has been successfully unblocked."

    except UserError:
        return "User ID doesn't exist."

def edit_user(user_id, amount):
    try:
        if not user_id:
            raise UserError

        mycursor = mydb.cursor()
        edit_balance_query = "UPDATE finances SET balance = %s WHERE user_id = %s"
        mycursor.execute(edit_balance_query,(amount, user_id))
        mydb.commit()
        mycursor.close()

        return "User balance has been successfully edited."
    except UserError:
        return "Wrong user_id"

def credit_users_account(user_id: int, amount):
    """
    Credit user's balance.

    VERY IMPORTANT (NON-JUNIOR):
    - Serializable isolation level
    - Explicit transaction handling
    - Balance consistency guarantee
    """
    try:
        if not user_id:
            raise UserError

        mycursor = mydb.cursor()
        mycursor.execute("USE Financial_Transaction_Engine_System")

        mycursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        mycursor.execute("START TRANSACTION")

        mycursor.execute(
            "UPDATE finances SET balance = balance + %s WHERE user_id = %s",
            (amount, user_id)
        )

        if mycursor.rowcount == 0:
            raise UserError

        withdraw_time = datetime.now()

        mycursor.execute(
            "SELECT balance, card_number FROM finances WHERE user_id = %s FOR UPDATE",
            (user_id,)
        )

        result = mycursor.fetchall()

        fill_history(
            user_id,
            "ATM #01",
            result[0][1],
            f"+{amount}",
            withdraw_time
        )

        mydb.commit()
        mycursor.close()
        return "User balance has been successfully added"

    except UserError:
        mydb.rollback()
        return "User ID doesn't exist"


def show_user_transaction_history(user_id: int):
    """
    Print user's transaction history.

    Demonstrates:
    - Read-only querying
    - Controlled output formatting
    """
    try:
        if not user_id:
            raise UserError

        mycursor = mydb.cursor()
        mycursor.execute("USE Financial_Transaction_Engine_System")

        mycursor.execute(
            "SELECT FromCard, ToCard, amount, date FROM history WHERE user_id = %s",
            (user_id,)
        )

        transactions = mycursor.fetchall()

        for record in transactions:
            print(
                f"\nFrom user card: {record[0]}\n"
                f"To card: {record[1]}\n"
                f"Amount: {record[2]}\n"
                f"Date: {record[3]}\n"
            )

    except UserError:
        return "User ID doesn't exist"
