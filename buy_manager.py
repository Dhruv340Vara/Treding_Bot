class BuyManager:
    def __init__(self, api):
        self.api = api
        self.executed_orders = set()

    def get_ltp(self, exchange, symbol, token):
        data = self.api.ltpData(exchange, symbol, token)

        if not data.get("status"):
            return None

        return float(data['data']['ltp'])

    def place_buy_order(self, symbol, token, exchange, quantity):

        params = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": "BUY",
            "exchange": exchange,
            "ordertype": "MARKET",
            "producttype": "DELIVERY",
            "duration": "DAY",
            "price": "0",
            "squareoff": "0",
            "stoploss": "0",
            "quantity": str(quantity),
            "scripconsent":"yes"
        }

        return self.api.placeOrder(params)

    def auto_buy(self, buy_orders=[]):

        for order in buy_orders:

            try:
                symbol = order["symbol"]
                token = order["token"]
                exchange = order["exchange"]

                entry_price = float(order["entry_price"])
                qty = int(order["qty"])

                key = f"{symbol}_{entry_price}"

                if key in self.executed_orders:
                    continue

                ltp = self.get_ltp(exchange, symbol, token)

                if ltp is None:
                    continue

                print(f"{symbol} | LTP: {ltp} | ENTRY: {entry_price}")

                if ltp <= entry_price:

                    print(f"🟢 BUY TARGET HIT → {symbol}")

                    res = self.place_buy_order(symbol,token,exchange,qty)

                    print("✅ BUY ORDER:", res)

                    self.executed_orders.add(key)

            except Exception as e:
                print("⚠️ Buy Error:", e)
