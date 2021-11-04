from cs50 import SQL

from tempfile import mkdtemp
# from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
# from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
import entities.transaction
import hashlib
import time

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


def create_transaction(transaction, user_funds, config):
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
    transaction_hash = hashlib.sha256(
        str(transaction.type).encode('utf-8') +
        str(transaction.user_id).encode('utf-8') +
        str(transaction.purchase_value).encode('utf-8') +
        str(transaction.currency).encode('utf-8') +
        str(transaction.stock_no).encode('utf-8') +
        str(transaction.stock_symbol).encode('utf-8') +
        str(transaction.exchange_id).encode('utf-8') +
        str(time.time()).encode('utf-8')
    ).hexdigest()

    print(transaction_hash)

    transaction.transaction_hash = transaction_hash

    if not config.db.execute("SELECT 1 FROM transactions WHERE transaction_hash = ?", transaction_hash):
        transaction_id = config.db.execute("INSERT INTO transactions " +
            "(type, user_id, purchase_value, currency, stock_no, stock_symbol, exchange_id, complete, transaction_hash) " +
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            transaction.type,
            transaction.user_id,
            transaction.purchase_value,
            transaction.currency,
            transaction.stock_no,
            transaction.stock_symbol,
            transaction.exchange_id,
            1,
            transaction.transaction_hash
        )

        if transaction_id:
            # update user table, minus the value of transaction itself
            if transaction.type == "BUY":
                updated_user_funds = float(user_funds) - float(transaction.purchase_value)
            else:
                updated_user_funds = float(user_funds) + float(transaction.purchase_value)
            # minus funds from user, based on their purchase
            user_update = config.db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_user_funds, transaction.user_id)

            data["success"] = True
            data["data"] = {
                "transaction_id": transaction_id,
                "user_update": user_update
            }
            return data
        else:
            data["success"] = False
            data["error"] = "Error has occured"
            return data


    data["success"] = False
    data["error"] = "Transaction already exists"
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

    transaction_amount = float(stock_price) * float(no_of_stocks)

    funds = config.db.execute("SELECT cash FROM users WHERE id = ? AND cash >= ?", user_id, transaction_amount)

    if funds:
        data["success"] = True
        data["data"] = {
            "user_wallet": float(funds[0]['cash']),
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

    exchange = config.db.execute("SELECT id FROM exchanges WHERE name LIKE ?", exchange_name)

    if exchange:
        data["success"] = True
        data["data"] = {
            "exchange_id": exchange[0]["id"]
        }
        return data
    else:
        data["success"] = False
        data["error"] = True
        data["error"] = "Exchange not found in database"
        return data

def get_user_stocks(user_id, config):
    data = {
        "error": False,
        "success": False,
        "data": False,
    }

    stocks = config.db.execute("SELECT SUM(purchase_value) AS purchase_value, SUM(stock_no) AS no_of_stocks, stock_symbol FROM transactions WHERE user_id = ? AND type = 'BUY' AND complete = 1 GROUP BY stock_symbol", user_id)

    if stocks:
        data["success"] = True
        data["data"] = {
            "stocks": stocks
        }
        return data
    else:
        data["success"] = False
        data["error"] = "Stocks not found in database"
        data["data"] = {
            "stocks": ""
        }
        return data

def get_user_transaction_history(user_id, config, completed = 1):
    data = {
        "error": False,
        "success": False,
        "data": False,
    }

    # work on using range to get data as chunks
    transactions = config.db.execute("SELECT * FROM transactions WHERE user_id = ? AND complete = ?;", user_id, completed)

    if transactions:
        data["success"] = True
        data["data"] = {
            "transactions": transactions
        }
        return data
    else:
        data["success"] = False
        data["error"] = "No transaction found for user"
        data["data"] = {
            "transactions": ""
        }
        return data

def get_user_stock_by_symbol(user_id, stock_symbol, config):
    data = {
        "error": False,
        "success": False,
        "data": False,
    }

    stock_bought = config.db.execute("SELECT SUM(stock_no) AS no_of_stocks FROM transactions WHERE user_id = ? AND type = 'BUY' AND stock_symbol = ? AND complete = 1 GROUP BY stock_symbol", user_id, stock_symbol)
    stock_sold = config.db.execute("SELECT SUM(stock_no) AS no_of_stocks FROM transactions WHERE user_id = ? AND type = 'SELL' AND stock_symbol = ? AND complete = 1 GROUP BY stock_symbol", user_id, stock_symbol)

    if not stock_bought:
        stock_bought = 0
    else:
        stock_bought = stock_bought[0]["no_of_stocks"]

    if not stock_sold:
        stock_sold = 0
    else:
        stock_sold = stock_sold[0]["no_of_stocks"];

    current_stock = stock_bought - stock_sold

    if current_stock:
        data["success"] = True
        data["data"] = {
            "current_stock": current_stock
        }
        return data
    else:
        data["success"] = False
        data["error"] = "Stocks not found in database"
        data["data"] = {
            "current_stock": ""
        }
        return data

def get_current_user_cash(user_id, config):
    data = {
        "error": False,
        "success": False,
        "data": False,
    }

    funds = config.db.execute("SELECT cash FROM users WHERE id = ?", user_id)

    if funds:
        data["success"] = True
        data["data"] = {
            "cash": funds[0]["cash"]
        }
        return data
    else:
        data["success"] = False
        data["error"] = "Cannot find users cash"
        data["data"] = {
            "cash": ""
        }
        return data