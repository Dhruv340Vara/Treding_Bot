from angel_api import AngelOneAPI


class SearchToken:
    def __init__(self):
        angel = AngelOneAPI()

        # login karo
        if angel.login():
            self.obj = angel.get_api()
        else:
            self.obj = None

    def searchScrip(self, exchange, stock_name):

        if not self.obj:
            print("API not connected")
            return None

        try:
            data = self.obj.searchScrip(exchange, stock_name)

            if data['status'] and data['data']:

                for item in data['data']:
                    print(f"""
Symbol      : {item['tradingsymbol']}
Token       : {item['symboltoken']}
Exchange    : {item['exchange']}
Name        : {item['symbolname']}
""")

                return data['data'][0]['symboltoken']

            else:
                print("No stock found")
                return None

        except Exception as e:
            print("Error:", e)
            return None


# ===== RUN =====

api = SearchToken()

token = api.searchScrip("NSE", "KISSHT")

print("Fetched Token:", token)
