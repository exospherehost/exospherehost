from datetime import datetime

async def trigger_cron():
    print(f"From trigger_cron: {datetime.now()}")