# Financial Transaction Engine System

A backend system for managing users, authentication, and financial transactions such as withdrawals, transfers, and balance operations.

This project focuses on **security**, **data consistency**, and **clear separation of responsibilities** between validation, execution, and persistence layers.

---

## 📌 Features

- User management (update profile data, block/unblock, delete)
- Secure authentication using JWT
- Withdrawal and transfer validation
- Balance crediting with transaction isolation
- Transaction history logging
- Role-based restrictions (admin vs user)
- Account locking support
- MySQL database with transactional safety


---

## 🔐 Authentication & Authorization

- JWT is used for authentication.
- Each protected operation decodes the token to extract:
  - `user_id`
  - `role`
- Admin users are **restricted from performing transfers**.
- Blocked users are prevented from:
  - Withdrawals
  - Transfers
  - Balance-related actions

---

## 💸 Transactions Logic

### Withdraw Validation
Handled in `transaction_validation.py`

Validation includes:
- Account lock status
- Balance sufficiency
- Defensive checks before database writes

### Transfer Validation
Validates:
- Sender identity via JWT
- Sender role
- Sender balance
- Sender account status
- Receiver existence
- Receiver account status

Only validation happens here — **no balance updates**.

---

## 🧾 Transaction History

- All financial operations are logged in a `history` table
- Implemented in `history_model.py`
- History logging is **decoupled** from transaction logic
- Supports auditing and traceability

---

## 🛡️ Data Consistency & Safety

- Explicit SQL transactions
- Serializable isolation level for balance updates
- Foreign key checks handled manually during deletion
- Rollbacks on failure
- Row count checks to detect invalid operations

---

## 🗄️ Database

- MySQL
- Explicit database selection (`USE Financial_Transaction_Engine_System`)
- Tables used:
  - `users`
  - `security`
  - `finances`
  - `history`

---

## ⚠️ Error Handling

Custom exceptions are used for clarity:
- `UserError`
- `BlockedUserError`
- `InsufficientFundsError`
- `EmailError`
- `PhoneNumberError`
- `AgeError`
- `UnknownError`

This keeps business logic readable and predictable.

---

## 🧠 Design Decisions 

- Separation of concerns (validation vs execution vs persistence)
- JWT-based authorization inside business logic
- Transaction isolation for financial safety
- Explicit commit/rollback handling
- Defensive validation order
- Audit-friendly history logging
- Clear responsibility per module

---

## 🚀 How to Run

1. Configure database connection in `app/config/mydb.py`
2. Ensure MySQL database and tables exist
3. Install dependencies:
   ```bash
   pip install phonenumbers PyJWT
