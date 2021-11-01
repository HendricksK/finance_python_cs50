import urllib.request, json
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session

import requests

from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

def query(url):
    # https://misscoded.com/flask-external-apis/
    data = {
        "error": False,
        "success": False,
        "data": False,
    }

    resp = requests.get(url)

    if not resp.status_code == 200:
        data["success"] = False
        # TODO log error in DB
        data["data"] = "An error has occured"
    else:
        data["success"] = True
        data["data"] = resp.json()

    return data

def mostactive_stocks(base_url, api_key):

    data = {
        "error": False,
        "success": False,
        "data": False,
    }

    url = base_url + "/stable/stock/market/list/mostactive?token=" + api_key

    response = query(url)

    if not response["success"]:
        data["error"] = True
        data["data"] = "An error has occured"
    else:
        data["success"] = True
        data["data"] = response["data"]

    return data

def quote_stock(stock_symbol, base_url, api_key):

    data = {
        "error": False,
        "success": False,
        "data": False,
    }

    url = base_url + "/stable/stock/" + stock_symbol + "/quote?token=" + api_key

    response = query(url)

    if not response["success"]:
        data["error"] = True
        data["data"] = "An error has occured"
    else:
        data["success"] = True
        data["data"] = response["data"]

    return data

def get_exchanges(base_url, api_key):
    data = {
        "error": False,
        "success": False,
        "data": False,
    }

    url = base_url + "/stable/ref-data/exchanges?token=" + api_key

    response = query(url)

    if not response["success"]:
        data["error"] = True
        data["data"] = "An error has occured"
    else:
        data["success"] = True
        data["data"] = response["data"]

    return data

def get_stock_curr_price(base_url, api_key, symbol):
    #https://cloud.iexapis.com/stable/stock/twtr/quote/latestPrice?token=
    data = {
        "error": False,
        "success": False,
        "data": False,
    }

    url = base_url + "/stable/stock/" + symbol + "/quote/latestPrice?token=" + api_key

    response = query(url)

    print(response)

    if not response["success"]:
        data["error"] = True
        data["data"] = "An error has occured"
    else:
        data["success"] = True
        data["data"] = response["data"]

    return data

def get_stock_variable(base_url, api_key, symbol, variable):
    #https://cloud.iexapis.com/stable/stock/twtr/quote/latestPrice?token=
    data = {
        "error": False,
        "success": False,
        "data": False,
    }

    # add array of variables we can get

    url = base_url + "/stable/stock/" + symbol + "/quote/" + variable + "?token=" + api_key

    response = query(url)

    print(response)

    if not response["success"]:
        data["error"] = True
        data["data"] = "An error has occured"
    else:
        data["success"] = True
        data["data"] = response["data"]

    return data