"""
Transaction validation module.

This module is responsible for validating:
- Withdraw operations
- Transfer operations between users

It does NOT perform balance updates or transfers itself.
Only validation logic lives here.

- Separation of concerns:
  validation is isolated from execution logic.
"""

from app.config import mydb
from app.services.auth_service import user_jwt
from app.services.possible_errors import (
    InsufficientFundsError,
    BlockedUserError,
    UserError
)
from app.utils.jwt_utils import decode_jwt


def withdraw_validation(user_id: str, amount: str, user_status: int) -> bool | int:
    """
    Validate whether a withdrawal operation is allowed.

    Parameters:
    - user_id: ID of the user requesting withdrawal
    - amount: withdrawal amount
    - user_status: account lock status (1 = blocked)

    Return values:
    - True  -> withdrawal allowed
    - False -> insufficient funds
    - 1     -> user is blocked

    Highlights:
    - Business rule validation before DB write
    - Explicit return codes instead of silent failure
    """
    try:
        # Security-level validation (non-junior: checked before DB queries)
        if user_status == 1:
            raise BlockedUserError

        mycursor = mydb.cursor()
        mycursor.execute("USE Financial_Transaction_Engine_System")

        balance_query = "SELECT balance FROM finances WHERE user_id = %s"
        mycursor.execute(balance_query, (user_id,))
        balance = mycursor.fetchone()[0]

        # Explicit numeric comparison avoids float precision issues
        if int(balance) < int(amount):
            raise InsufficientFundsError
        else:
            mycursor.close()
            return True

    except InsufficientFundsError:
        return False
    except BlockedUserError:
        return 1


def transfer_validation(to_card: str, amount: str) -> int:
    """
    Validate money transfer operation.

    Validations performed:
    - JWT validity and sender identity
    - Sender role (admin transfers are blocked)
    - Sender account status
    - Sender balance sufficiency
    - Receiver existence and account status

    Return values:
    - receiver_user_id -> transfer allowed
    - 0 -> invalid user / unauthorized
    - 1 -> blocked account (sender or receiver)
    - 2 -> insufficient funds

    Highlights (VERY NOT JUNIOR):
    - JWT-based authorization
    - Multi-user security checks
    - Defensive validation order
    """
    try:
        # Decode JWT to extract sender identity and role
        decoded_jwt = decode_jwt(user_jwt[0])
        sender_user_id = decoded_jwt['user_id']
        user_role = decoded_jwt['role']

        # Admins are not allowed to perform transfers
        if user_role == ('admin',) or sender_user_id == "":
            raise UserError

        mycursor = mydb.cursor()
        mycursor.execute("USE Financial_Transaction_Engine_System")

        # Check sender account lock status
        query_account_locking = (
            "SELECT account_locked FROM security WHERE user_id = %s;"
        )
        mycursor.execute(query_account_locking, (sender_user_id,))
        sender_status = mycursor.fetchone()[0]

        # Fetch sender balance
        sender_balance_query = (
            "SELECT balance FROM finances WHERE user_id = %s;"
        )
        mycursor.execute(sender_balance_query, (sender_user_id,))
        sender_balance = mycursor.fetchone()[0]

        if sender_status == 1:
            raise BlockedUserError
        elif int(sender_balance) < int(amount):
            raise InsufficientFundsError

        # Fetch receiver user ID by card number
        reciver_id_query = (
            "SELECT user_id FROM finances WHERE card_number = %s;"
        )
        mycursor.execute(reciver_id_query, (to_card,))
        reciver_user_id = mycursor.fetchone()[0]

        # Check receiver account lock status
        reciver_status_query = (
            "SELECT account_locked FROM security WHERE user_id = %s;"
        )
        mycursor.execute(reciver_status_query, (reciver_user_id,))
        reciver_status = mycursor.fetchone()[0]

        if reciver_status == 1:
            raise BlockedUserError

        # Returning receiver ID allows the transfer logic
        # to stay clean and focused
        return reciver_user_id

    except UserError:
        return 0
    except BlockedUserError:
        return 1
    except InsufficientFundsError:
        return 2
