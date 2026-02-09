"""
Transaction history persistence module.

Responsible ONLY for saving transaction records.
No validation of business rules happens here.

- History logging is isolated from transaction logic
- Allows auditing and rollback analysis
"""

from app.config import mydb
from app.services.possible_errors import UnknownError


def fill_history(user_id, from_card, to_card, amount, date):
    """
    Insert a transaction record into history table.

    Parameters:
    - user_id: ID of the user performing the transaction
    - from_card: source card number
    - to_card: destination card number
    - amount: transaction amount (with + / - sign if needed)
    - date: transaction datetime

    Highlights:
    - Defensive input presence checks
    - Explicit DB transaction control
    """
    try:
        # Basic presence validation before DB interaction
        if not str(from_card).strip():
            raise UnknownError
        if not str(to_card).strip():
            raise UnknownError
        if not str(amount).strip():
            raise UnknownError
        if not str(date).strip():
            raise UnknownError

        mycursor = mydb.cursor()
        mycursor.execute("USE Financial_Transaction_Engine_System")

        history_query = (
            "INSERT INTO history(user_id, FromCard, ToCard, amount, date) "
            "VALUES (%s, %s, %s, %s, %s)"
        )

        mycursor.execute(
            history_query,
            (user_id, from_card, to_card, amount, date)
        )

        mydb.commit()
        mycursor.close()
        return "History has been successfully added"

    except UnknownError:
        mydb.rollback()
        return "You missed to fill some info"
