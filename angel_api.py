import os
from dotenv import load_dotenv
import pyotp
from SmartApi import SmartConnect


class AngelOneAPI:
    def __init__(self):
        load_dotenv("config.env")

        self.api_key = os.getenv("API_KEY")
        self.client_id = os.getenv("CLIENT_ID")
        self.password = os.getenv("PASSWORD")
        self.totp_secret = os.getenv("TOTP_SECRET")

        self.api = None

    def generate_totp(self):
        return pyotp.TOTP(self.totp_secret).now()

    def login(self):
        try:
            self.api = SmartConnect(api_key=self.api_key)

            data = self.api.generateSession(
                self.client_id,
                self.password,
                self.generate_totp()
            )

            if not data.get("status"):
                print("❌ Login Failed:", data)
                return False

            print("✅ Login Successful")
            return True

        except Exception as e:
            print("⚠️ Error:", str(e))
            return False

    def get_api(self):
        return self.api
