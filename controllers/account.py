from cs50 import SQL

from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
# TODO: implement use of entities/users.py
# TODO: implement use of entities/account.py

def account_login(username, password, config):


    # Query database for username
    rows = False
    rows = config.db.execute("SELECT id, hash FROM users WHERE username = ?", username)
    data = {
        "error": False,
        "success": False,
        "data": False,
    }

    # Ensure username exists and password is correct
    if len(rows) > 0 and not check_password_hash(rows[0]["hash"], password):
        # https://docs.python.org/3/tutorial/datastructures.html#dictionaries
        data["error"] = "Invalid username and/or password"
        return data

    # Remember which user has logged in
    if len(rows) > 0:
        data["success"] = True
        data["data"] = {"user_id":rows[0]["id"]}
        return data
    else:
        data["error"] = "No user found"
        return data


def account_register(username, password, config):
    # generate_password_hash https://werkzeug.palletsprojects.com/en/1.0.x/utils/#werkzeug.security.generate_password_hash
    # No need for batch updates here, as users are single creation only.

    data = {
        "error": False,
        "success": False,
        "data": False,
    }

    if not config.db.execute("SELECT 1 FROM users WHERE username = ?", username):
        user_hash = generate_password_hash(password)
        if config.db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, user_hash):
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
def account_password_forgot():
    pass

# TODO: Create a log table, log all user interactions, login, register, logout etc
def log(user):
    pass



