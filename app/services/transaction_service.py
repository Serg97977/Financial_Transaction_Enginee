"""
Transaction Service Module
--------------------------
Manages critical financial operations including cash withdrawals and
peer-to-peer money transfers.

Security & Integrity:
- Implements 'SERIALIZABLE' isolation levels to prevent race conditions.
- Uses database Transactions (BEGIN/COMMIT/ROLLBACK) to ensure ACID compliance.
- Integrates with history_model to maintain an immutable audit trail.
"""

from app.services.possible_errors import UserError, BlockedUserError, InsufficientFundsError
from app.models.transaction_validation import transfer_validation, withdraw_validation
from app.models.history_model import fill_history
from app.services.auth_service import user_jwt
from app.utils.jwt_utils import decode_jwt
from datetime import datetime
from app.config import mydb


def withdraw(amount: str) -> str:
    """
    Deducts a specified amount from the user's balance.

    Logic:
    1. Authenticates user via JWT.
    2. Starts a Serializable transaction.
    3. Validates funds and account status (Locked/Active).
    4. Updates balance and logs the event in transaction history.
    """
    try:
        decoded_jwt = decode_jwt(user_jwt[0])
        user_id = decoded_jwt['user_id']
        user_role = decoded_jwt['role']

        # Guard: Prevent admin or unauthenticated access
        if user_role == ('admin',) or user_id == "":
            raise UserError

        mycursor = mydb.cursor()
        mycursor.execute("USE Financial_Transaction_Engine_System")

        # Set highest isolation level to prevent Double-Spending during concurrent requests
        mycursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        mycursor.execute("START TRANSACTION")

        user_status_query = "SELECT account_locked FROM security WHERE user_id = %s"
        mycursor.execute(user_status_query, (user_id,))
        status = mycursor.fetchone()[0]

        # Business logic validation
        result = (withdraw_validation(user_id, amount, status))
        if result == False:
            mydb.rollback()
            return "The bank rejected the payment because of insufficient funds."
        elif result == "1":
            mydb.rollback()
            return "You bank account is blocked."
        else:
            # Atomic update of balance
            balance_query = "UPDATE finances SET balance = balance - %s WHERE user_id = %s"
            mycursor.execute(balance_query, (amount, user_id))

            withdraw_time = datetime.now()
            mydb.commit()  # End transaction successfully

            # Fetch final state for history logging
            new_balance_query = "SELECT balance, card_number FROM finances WHERE user_id = %s FOR UPDATE"
            mycursor.execute(new_balance_query, (user_id,))
            result = mycursor.fetchall()

            # Log to history table
            fill_history(user_id, result[0][1], 0, "-" + amount, withdraw_time)
            mycursor.close()

        return f"Now in your balance: {result[0][0]}"

    except UserError:
        return "Something went wrong."


def transaction(to_card: str, amount: str) -> str:
    """
    Handles peer-to-peer transfers between two card numbers.

    Logic:
    1. Subtracts amount from sender.
    2. Adds amount to receiver (identified via card number).
    3. Creates two history entries (Debit for sender, Credit for receiver).
    """
    try:
        decoded_jwt = decode_jwt(user_jwt[0])
        sender_user_id = decoded_jwt['user_id']
        user_role = decoded_jwt['role']
        if user_role == ('admin',) or sender_user_id == "":
            raise UserError

        mycursor = mydb.cursor()
        mycursor.execute("USE Financial_Transaction_Engine_System")

        # Get sender's card number for the history record
        sender_card_number_query = "SELECT card_number FROM finances WHERE user_id = %s"
        mycursor.execute(sender_card_number_query, (sender_user_id,))
        sender_card_number = mycursor.fetchone()[0]

        mycursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        mycursor.execute("START TRANSACTION")

        # Validate receiver existence, amount, and sender status
        validation_result = transfer_validation(to_card, amount)
        if validation_result == 0:
            mydb.rollback()
            return "Error: Something went wrong"
        elif validation_result == 1:
            mydb.rollback()
            return "Error: User account has been blocked"
        elif validation_result == 2:
            mydb.rollback()
            return "Error: The bank rejected the payment because of insufficient funds."

        # Perform the dual-update (The core of the transaction)
        sending_money_query = "UPDATE finances SET balance = balance - %s WHERE user_id = %s;"
        mycursor.execute(sending_money_query, (amount, sender_user_id))

        receive_money_query = "UPDATE finances SET balance = balance + %s WHERE user_id = %s;"
        mycursor.execute(receive_money_query, (amount, validation_result))  # validation_result = receiver_id

        transaction_time = datetime.now()

        # Log history for both parties
        fill_history(sender_user_id, sender_card_number, to_card, "-" + amount, transaction_time)
        fill_history(validation_result, to_card, sender_card_number, "+" + amount, transaction_time)

        mydb.commit()
        mycursor.close()

        return "Money successfully transacted."

    except (UserError, BlockedUserError, InsufficientFundsError):
        # Note to dev: Specific exceptions are caught and returned as generic errors for security
        return "Error.."
