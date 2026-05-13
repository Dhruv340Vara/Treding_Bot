# sell_manager.py

class SellManager:
    def __init__(self, api):
        self.api = api
        self.executed_targets = set() 
    def get_holdings(self):
        data = self.api.holding()
        if not data.get("status"):
            return []
        return data['data']

    def get_ltp(self, exchange, symbol, token):
        data = self.api.ltpData(exchange, symbol, token)
        if not data.get("status"):
            return None
        return float(data['data']['ltp'])

    def calculate_profit(self, avg, ltp):
        return ((ltp - avg) / avg) * 100

    def place_sell_order(self, symbol, token, exchange, quantity):
        params = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": "SELL",
            "exchange": exchange,
            "ordertype": "MARKET",
            "producttype": "DELIVERY",
            "duration": "DAY",
            "price": "0",
            "squareoff": "0",
            "stoploss": "0",
            "quantity": str(quantity)
        }
        return self.api.placeOrder(params)

    def auto_sell(self, target_profit=10, target_orders=[]):
        holdings = self.get_holdings()

        for stock in holdings:
            try:
                symbol = stock['tradingsymbol']
                token = stock['symboltoken']
                exchange = stock['exchange']

                quantity = int(stock.get('quantity', 0))
                avg_price = float(stock.get('averageprice', 0))
                
                if symbol == "JWL-EQ":
                    continue
                     
                ltp = self.get_ltp(exchange, symbol, token)
                if ltp is None:
                    continue
                    
                if quantity <= 0:
                    continue
                    
                target_hit = False

                for order in target_orders:
                    if order["symbol"] != symbol:
                        continue

                    key = f"{symbol}_{order['target_price']}"
                    if key in self.executed_targets:
                        continue

                    target_price = order["target_price"]
                    sell_qty = min(order["qty"], quantity)
                    #print(f"{symbol} | LTP:{ltp} | QTY:{sell_qty}")
                    if ltp >= target_price:
                        print(f"🎯 TARGET HIT → {symbol} @ {ltp}")

                        res = self.place_sell_order(symbol, token, exchange, sell_qty)
                        print("✅ Target Sell:", res)

                        self.executed_targets.add(key)
                        target_hit = True
                        break

                if target_hit:
                    continue
                profit = self.calculate_profit(avg_price, ltp)
                
                print(f"{symbol} | LTP: {ltp} | Profit: {profit:.2f}%")
                
                if any(order["symbol"] == symbol for order in target_orders):
                    continue

                if profit >= target_profit:
                    print(f"🚀 % Target Hit → Selling {symbol}")
                    res = self.place_sell_order(symbol, token, exchange, quantity)
                    print("✅", res)
                    continue

            except Exception as e:
                print("Stock Error:", e)
