import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta

from helpers import apology, login_required, lookup, usd
# user controller
from controllers.account import account_login, account_register
# iex controller
from controllers.iex import mostactive_stocks, quote_stock, get_stock_variable
# transaction controller, entity
from entities.transaction import Transaction
from controllers.transaction import get_user_transactions, create_transaction, check_user_affordability

# Finish up imports

# Configure application
app = Flask(__name__)
app.config.from_object("conf")
# Ensure templates are auto-reloaded
# Make sure API key is set
# https://flask.palletsprojects.com/en/2.0.x/config/
# Not going to set this the entire time via BASH
if not app.config["API_KEY"]:
    raise RuntimeError("API_KEY not set")

if not app.config["IEX_BASE_URL"]:
    raise RuntimeError("IEX_BASE_URL not set")

app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")
# Add DB to app config, usage across multiple files hopefully
app.config.db = db
# Add default currency to APP config
app.config.default_currency = "USD"

@app.route("/")
def index():
    if session.get("user_id") is None:
        return redirect("/login")

    """Show portfolio of stocks"""
    if not request.method == "GET":
        return apology("Forbidden", 403)
    else:
        return render_template("index.html")

@app.route("/buy", methods=["GET", "POST"])
def buy():
    """Buy shares of stock"""

    if session.get("user_id") is None:
        return redirect("/login")
    # Data needs to be git gud either way
    response = mostactive_stocks(app.config["IEX_BASE_URL"], app.config["API_KEY"])

    if not response["success"]:
        return render_template("buy.html",
            error="An error has occured",
            data=""
        )

    data = {
        "most_active_stocks": response["data"],
        "currency": app.config.default_currency
    }

    if request.method == "POST":
        symbol = request.form.get("stock-symbol")
        no_of_stocks = request.form.get("no-of-stock")

        stock_price = get_stock_variable(app.config["IEX_BASE_URL"], app.config["API_KEY"], symbol.lower(), "latestPrice")

        if not stock_price["success"]:
            return render_template("buy.html",
                    error="Could not retrieve stock price",
                    data=data
                )

        if not symbol or not no_of_stocks:
            return render_template("buy.html",
                error="bitch better have my money",
                data=data,
                single_stock=False)
        else:
            # start actual data manipulation
            user_funds = check_user_affordability(stock_price["data"], no_of_stocks, session.get("user_id"), app.config)

            if user_funds["success"]:
                stock_exchange_name = get_stock_variable(app.config["IEX_BASE_URL"], app.config["API_KEY"], symbol.lower(), "primaryExchange")
                exchange = get_exchange_id(stock_exchange_name, app.config)

                if exchange["success"]
                    exchange_id = exchange["data"].exchange_id
                else:
                    exchange_id = -99

                transaction = Transaction(
                    "BUY",
                    session.get("user_id"),
                    user_funds["data"].transaction_amount,
                    app.config.default_currency,
                    no_of_stocks,
                    symbol,
                    exchange_id, # 1 for now.
                    0)

                print(transaction)
            else:
                return render_template("buy.html",
                        error="An error has occured",
                        data=data
                    )
    else:
        return render_template("buy.html",
            error="",
            data=data)


@app.route("/history")
def history():

    if session.get("user_id") is None:
        return redirect("/login")

    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 403)

        # if user exists, set session
        data = account_login(username, password, app.config)

        if not data["success"]:
            return render_template("login.html", error=data["error"])
        else:
            session["user_id"] = data["data"]["user_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
def quote():
    """Get stock quote."""

    if session.get("user_id") is None:
        return redirect("/login")

    if request.method == "POST":
        symbol = request.form.get("stock-symbol")

        if not symbol:
            return render_template("quote.html",
                error="Please enter a valid stock",
                data="",
                single_stock=False)

        response = quote_stock(symbol, app.config["IEX_BASE_URL"], app.config["API_KEY"])

        if not response["success"]:
            return render_template("quote.html",
                error="An error has occured",
                data="",
                single_stock=False)
        else:
            data = {
                "stock_data": response["data"]
            }
            return render_template("quote.html",
                error="",
                data=data,
                single_stock=True)
    else:
        response = mostactive_stocks(app.config["IEX_BASE_URL"], app.config["API_KEY"])

        if not response["success"]:
            return render_template("quote.html",
                error="An error has occured",
                data="",
                single_stock=False
            )
        else:
            data = {
                "most_active_stocks": response["data"]
            }
            return render_template("quote.html",
                error="",
                data=data,
                single_stock=False)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        # Ensure username was submitted
        if not username:
            return render_template("register.html", error="Cannot create an account without a username")

        # Ensure password was submitted
        elif not password:
            return render_template("register.html", error="Cannot create an account without a password")

        # if user exists, set sessionls
        data = account_register(username, password, app.config)

        if not data["success"]:
            return render_template("register.html", error=data["error"])
        else:
            session["user_id"] = data["data"]["user_id"]

        # Redirect user to home page
        return redirect("/account.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

    # return apology("TODO")
    return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
def sell():

    if session.get("user_id") is None:
        return redirect("/login")

    """Sell shares of stock"""
    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
