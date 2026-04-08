import pandas as pd
import datetime
import time
from sqlalchemy import create_engine
from SmartApi import SmartConnect
import pyotp
from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path(__file__).resolve().parent.parent / ".env"

# .env load karo
load_dotenv(env_path)

api_key = os.getenv("API_KEY")
client_id = os.getenv("CLIENT_ID")
password = os.getenv("PASSWORD")
totp_secret = os.getenv("TOTP_SECRET")

db_url = os.getenv("DB_URL")

data_after = False

# 🔗 Login
obj = SmartConnect(api_key=api_key)
totp = pyotp.TOTP(totp_secret).now()
data = obj.generateSession(client_id, password, totp)

if not data or data.get('status') == False:
    print("❌ Login Failed")
    exit()

print("✅ Login Success")

# DB connection
engine = create_engine(db_url)
if(data_after):
    # DB mathi last time fetch
    query = "SELECT MAX(time) FROM jwl_data"
    last_time = pd.read_sql(query, engine).iloc[0, 0]

    if last_time is None:
        last_time = datetime.datetime(2026, 4, 1, 9, 14)
    else:
        last_time = pd.to_datetime(last_time)

    # next candle thi start
    start_date = last_time + datetime.timedelta(minutes=1)
    end_date = datetime.datetime.now()
else:
    # DB mathi first time fetch
    query = "SELECT MIN(time) FROM jwl_data"
    last_time = pd.read_sql(query, engine).iloc[0, 0]

    if last_time is None:
        last_time = datetime.datetime(2026, 4, 1, 9, 14)
    else:
        last_time = pd.to_datetime(last_time)

    # next candle thi start
    start_date = last_time - datetime.timedelta(days=30)
    end_date = last_time

all_data = []
current_date = start_date
# print(current_date , end_date)
while current_date < end_date:
    from_date = current_date.strftime("%Y-%m-%d 09:15")
    to_date = current_date.strftime("%Y-%m-%d 15:30")

    historicParam = {
            "exchange": "NSE",
            "symboltoken": "20224",
            "interval": "ONE_MINUTE",
            "fromdate": from_date,
            "todate": to_date
        }
        
    try:

        res = obj.getCandleData(historicParam)

        if res and res.get('status') and isinstance(res.get('data'), list):
            all_data.extend(res['data'])
            print(f"Fetched: {from_date}")


    except Exception as e:
    	print("Error:", e)
	
    	log_data = {
        	"run_time": datetime.datetime.now(),
        	"start_date": start_date,
        	"end_date": end_date,
        	"rows_inserted": 0,
        	"status": "FAILED",
        	"message": str(e)
    	}
	
    	pd.DataFrame([log_data]).to_sql("jwl_data_log", engine, if_exists="append", index=False)
    time.sleep(0.5)
    current_date += datetime.timedelta(days=1)

# DataFrame
df = pd.DataFrame(all_data, columns=["time","open","high","low","close","volume"])

# ✅ Empty check
if df.empty:
    print("⚠️ No new data")
else:
    df['time'] = pd.to_datetime(df['time'])

    if df['time'].dt.tz is None:
        df['time'] = df['time'].dt.tz_localize('UTC')
    else:
        df['time'] = df['time'].dt.tz_convert('UTC')

# convert to IST
df['time'] = df['time'].dt.tz_convert('Asia/Kolkata')

# remove timezone
df['time'] = df['time'].dt.tz_localize(None)

last_time = pd.to_datetime(last_time)
last_time = last_time.replace(tzinfo=None)

# filter new data
if data_after:
    df = df[df['time'] > last_time]
else:
    df = df[df['time'] < last_time]

# remove duplicates
df = df.drop_duplicates(subset=['time'])
df = df.sort_values(by='time')

# insert
df.to_sql("jwl_data", engine, if_exists="append", index=False)

print("✅ Direct DB insert done:", df.shape)

log_data = {
    "run_time": datetime.datetime.now(),
    "start_date": start_date,
    "end_date": end_date,
    "rows_inserted": len(df),
    "status": "SUCCESS",
    "message": "Data inserted successfully"
}

log_df = pd.DataFrame([log_data])
log_df.to_sql("jwl_data_log", engine, if_exists="append", index=False)
