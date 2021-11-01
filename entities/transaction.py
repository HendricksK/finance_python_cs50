class Transaction:
    # https://www.w3schools.com/python/python_classes.asp
    def __init__(self, type, user_id, purchase_value, currency, stock_no, stock_symbol, exchange_id, complete):
        self.type = type
        self.user_id = user_id
        self.purchase_value = purchase_value
        self.currency = currency
        self.stock_no = stock_no
        self.stock_symbol = stock_symbol
        self.exchange_id = exchange_id
        self.complete = complete