from cs50 import SQL

from tempfile import mkdtemp
# from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
# from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
import entities.transaction
import hashlib

def get_user_transactions(user_id, config):

    # Query database for username
    rows = False
    rows = config.db.execute("SELECT id, hash FROM users WHERE username = ?", username)
    data = {
        "error": False,
        "success": False,
        "data": False,
    }

    # Ensure username exists and password is correct


    # Remember which user has logged in
    if len(rows) > 0:
        data["success"] = True
        data["data"] = {"user_id":rows[0]["id"]}
        return data
    else:
        data["error"] = "No user found"
        return data


def create_transaction(transaction, config):
    # generate_password_hash https://werkzeug.palletsprojects.com/en/1.0.x/utils/#werkzeug.security.generate_password_hash
    # No need for batch updates here, as users are single creation only.

    data = {
        "error": False,
        "success": False,
        "data": False,
    }
    # https://docs.python.org/3/library/hashlib.html
    # HASH entire transaction object, check if has is in DB if not insert
    # transactions can never be the same
    # DO NOT CHANGE
    transaction_hash = hashlib.sha256()
    transaction_hash.update(transaction)

    if not config.db.execute("SELECT 1 FROM transactions WHERE transaction_hash = ?", transaction_hash):
        if config.db.execute("INSERT INTO transactions (username, hash) VALUES (?, ?)", username, user_hash):
            # update user table, minus the value of transaction itself
            data["success"] = True
            data["data"] = {"user_id": db.lastrowid}
            return data
        else:
            data["success"] = False
            data["error"] = "Error has occured"
            return data


    data["success"] = False
    data["error"] = "Username already exists"
    return data


# TODO: Create forgot password implementation, recreate password for user
def get_transactions(config, no = 100):
    pass

def check_user_affordability(stock_price, no_of_stocks, user_id, config):
    # would prefer to have a wallet table here, and call data from wallet table / class entity and not cross class/entities
    # SELECT cash FROM "users" WHERE id = 1 AND cash > 2000;
    data = {
        "error": False,
        "success": False,
        "data": False,
    }

    print(stock_price)
    print(no_of_stocks)

    transaction_amount = float(stock_price) * float(no_of_stocks)

    print(transaction_amount)
    print(user_id)

    funds = config.db.execute("SELECT cash FROM users WHERE id = ? AND cash >= ?", user_id, transaction_amount)

    if funds:
        data["success"] = True
        data["data"] = {
            "user_wallet": float(funds),
            "transaction_amount": transaction_amount
        }
        return data
    else:
        data["success"] = False
        data["error"] = True
        data["error"] = "User does not have enough funds"
        return data

def get_exchange_id(exchange_name, config):
    data = {
        "error": False,
        "success": False,
        "data": False,
    }

    exchange = config.db.execute("SELECT id FROM exchanges WHERE name = ?", exchange_name)

    if funds:
        data["success"] = True
        data["data"] = {
            "exchange_id": exchange
        }
        return data
    else:
        data["success"] = False
        data["error"] = True
        data["error"] = "Exchange not found in database"
        return data