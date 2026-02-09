"""
Main Module: Banking System Engine
Version: 1.0.0

This module serves as the primary entry point for the banking application.
It manages the top-level Control Flow for three main branches:
1. User Authentication (Login)
2. User Registration (Onboarding)
3. Admin Log In (Admin Panel)

Dependencies:
- app.services: Contains business logic for users, admins, auth, and transactions.
"""

from app.services.admin_functions import *
from app.services.user_functions import *
from app.services.auth_service import register
from app.services.auth_service import login_admin
from app.services.auth_service import login
from app.services.user_service import save
from app.services.transaction_service import withdraw
from app.services.transaction_service import transaction

# Main Application Loop: Keeps the program running until a break condition is met
while True:
    logining_creating = input('1-Log In :\n'
                              '2-Create an account :\n'
                              '3-Admin Login :\n'
                              'ENTER ------->')

    # --- SECTION 1: USER LOGIN & DASHBOARD ---
    if logining_creating == '1':
        input_email = input("Enter your e-mail: ")
        input_password = input("Enter your password: ")

        login = login(input_email.upper(), input_password)
        print(login)

        if login == "Successful Login.":
            # Authenticated Session Loop
            while True:
                user_request = input("\n\n Show...\n"
                                     "1-BALANCE : \n"
                                     "2-TRANSACTION HISTORY : \n"
                                     "3-PROFILE : \n"
                                     "\nFINANCIAL TRANSACTION...\n\n"
                                     "4-MONEY TRANSFER : \n"
                                     "5-WITHDRAW MONEY : \n"
                                     "\nSETTINGS... \n\n"
                                     "7-CHANGE PHONE NUMBER : \n"
                                     "8-CHANGE EMAIL : \n"
                                     "9-CHANGE PASSWORD : \n"
                                     "ENTER NUMBER :::::::"
                                     )

                if user_request == "1":
                    print(show_balance())
                elif user_request == "2":
                    print(show_transaction_history())
                elif user_request == "3":
                    print(show_profile())
                elif user_request == "4":
                    card_num = input("Enter card number: ")
                    amount = input("Enter amount: ")
                    print(transaction(card_num, amount))
                elif user_request == "5":
                    amount = (input("Enter amount: "))
                    print(withdraw(amount))
                elif user_request == "7":
                    new_number = input("Enter your new number: ")
                    print(change_number(new_number))
                elif user_request == "8":
                    new_email = input("Enter your new e-mail: ")
                    print(change_email(new_email))
                elif user_request == "9":
                    print(change_password())

        else:
            break

    # --- SECTION 2: REGISTRATION ---
    elif logining_creating == '2':
        name = input("Enter your name: ")
        surname = input("Enter your surname: ")
        birth_date = input("Enter your birth date\n"
                           "FORM -> dd-mm-yyyy::: ")
        email = input("Enter your email: ")
        phone = input("Enter your phone number:\n"
                      "FORM -> +374 XX XXX XXX::: ")

        # Data is normalized to uppercase for email and names before saving
        result = register(name.upper(), surname.upper(), birth_date, email.upper(), phone)
        print(result)
        print(save(result))
        break

    # --- SECTION 3: ADMINISTRATIVE PANEL ---
    elif logining_creating == '3':
        admin_email = input('Enter admin email:\n')
        admin_password = input('Enter admin secret password: ')

        # Admin authentication logic
        login_adm = login_admin = login_admin(admin_email, admin_password)
        print(login_adm)

        if login_adm == "Successful Login.":
            # Administrative Action Loop
            while True:
                admin_request = input('\n\nMANAGE USERS\n'
                                      '1-VIEW ALL USERS: \n'
                                      '2-EDIT USER: \n'
                                      '3-DELETE USER: \n'
                                      '4-BLOCK/UNBLOCK USER: \n'
                                      '5-SHOW USER HISTORY: \n'
                                      '\n\n MANAGE TRANSACTIONS \n'
                                      '6-VIEW ALL TRANSACTIONS: \n'
                                      "7-TOP UP USER'S ACCOUNT: \n"
                                      'ENTER YOUR NUMBER: ')

                if admin_request == "1":
                    print(show_users())
                elif admin_request == "2":
                    # Sub-loop for targeted user attribute modifications
                    while True:
                        admin_subquery = input("\n1-Edit user name\n"
                                               "2-Edit user surname\n"
                                               "3-Edit user email\n"
                                               "4-Edit user phone number\n"
                                               "5-Edit user birth date\n"
                                               "6-Edit user balance\n"
                                               "ENTER YOUR NUMBER: ")
                        if admin_subquery == "1":
                            new_name = input("Enter new name: ")
                            user_id = input("Enter user id: ")
                            print(change_user_name(new_name, user_id))

                        elif admin_subquery == "2":
                            new_surname = input("Enter new surname: ")
                            user_id = input("Enter user id: ")
                            print(change_user_surname(new_surname, user_id))

                        elif admin_subquery == "3":
                            new_email = input("Enter new email: ")
                            user_id = input("Enter user id: ")
                            print(change_user_email(new_email, user_id))

                        elif admin_subquery == "4":
                            new_number = input("Enter new phone number: ")
                            user_id = input("Enter user_id: ")
                            print(change_user_number(new_number, user_id))

                        elif admin_subquery == "5":
                            new_birth_date = input("Enter new birth date: \n"
                                                   "FORM -> dd-mm-yyyy::: ")
                            user_id = input("Enter user_id: ")
                            print(change_user_birth_date(new_birth_date, user_id))

                        elif admin_subquery == "6":
                           user_id = input("Enter user id: ")
                           amount = input("Enter balance: ")
                           print(edit_user(user_id, amount))
                elif admin_request == "3":
                    user_id = input("Enter user id: ")
                    print(delete_user(user_id))

                elif admin_request == "4":
                    # Toggle user account access status
                    admin_subrequest = input("1-BLOCK:\n"
                                             "2-UNBLOCK:\n"
                                             "Enter 1/2----> ")
                    if admin_subrequest == "1":
                        user_id = input("Enter user id: ")
                        print(block_user(user_id))
                    elif admin_subrequest == "2":
                        user_id = input("Enter user id: ")
                        print(unblock_user(user_id))

                elif admin_request == "5":
                    user_id = input("Enter user id: ")
                    print(show_user_transaction_history(user_id))

                elif admin_request == "6":
                    # Direct account crediting functionality
                    user_id = input("Enter user_id: ")
                    amount = input("Enter amount: ")
                    print(credit_users_account(user_id, amount))

#sergeynorekyan6@gmail.com
#AdminPassword123