import time

from angel_api import AngelOneAPI
from scheduler import MarketScheduler
from buy_manager import BuyManager
print("program start")

if __name__ == "__main__":

    angel = AngelOneAPI()

    buy_orders = [
        {"symbol": "KISSHT-EQ","token": "763294","exchange": "NSE","entry_price": 209,"qty": 5}
    ]

    if angel.login():

        api = angel.get_api()

        buyer = BuyManager(api)

        scheduler = MarketScheduler()

        while True:

            try:

                if scheduler.is_market_open():

                    print("🟢 Market Open → Running Buy Algo")

                    buyer.auto_buy(buy_orders)

                    time.sleep(5)

                else:

                    sleep_sec = scheduler.seconds_until_next_open()

                    readable = scheduler.pretty_sleep_time(sleep_sec)

                    print(f"🔴 Market Closed → Sleeping for {readable}")

                    time.sleep(sleep_sec)

            except Exception as e:

                print("⚠️ Main Loop Error:", e)

                time.sleep(10)
                if angel.login():
                    api = angel.get_api()
                    buyer = BuyManager(api)

