from datetime import datetime, timedelta

class MarketScheduler:

    def is_market_open(self):
        now = datetime.now().time()
        return now >= datetime.strptime("09:00", "%H:%M").time() and \
               now <= datetime.strptime("15:30", "%H:%M").time()

    def seconds_until_next_open(self):
        now = datetime.now()
        today_open = now.replace(hour=9, minute=15, second=0, microsecond=0)

        if now.time() < today_open.time():
            return (today_open - now).total_seconds()

        next_open = today_open + timedelta(days=1)
        return (next_open - now).total_seconds()

    def pretty_sleep_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
