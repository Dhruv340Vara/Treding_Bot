import time
from angel_api import AngelOneAPI
from sell_manager import SellManager
from scheduler import MarketScheduler


if __name__ == "__main__":
    angel = AngelOneAPI()
    target_orders = [
        {"symbol": "DCMSRIND-EQ", "target_price": 50, "qty":10 },
        {"symbol": "TMCV-EQ", "target_price": 446, "qty":1 }
    ]
    if angel.login():
        api = angel.get_api()

        seller = SellManager(api)
        scheduler = MarketScheduler()

        while True:
            try:
                if scheduler.is_market_open():
                    print("🟢 Market Open → Running Algo")
                    seller.auto_sell(target_profit=10, target_orders=target_orders)

                    time.sleep(5)

                else:
                    sleep_sec = scheduler.seconds_until_next_open()
                    readable = scheduler.pretty_sleep_time(sleep_sec)

                    print(f"🔴 Market Closed → Sleeping for {readable}")

                    time.sleep(sleep_sec)

            except Exception as e:
                print("⚠️ Main Loop Error:", e)
                time.sleep(10)
