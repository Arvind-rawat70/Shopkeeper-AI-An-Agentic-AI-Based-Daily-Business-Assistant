from pathlib import Path
import sys
from dotenv import load_dotenv
import os
from apscheduler.schedulers.blocking import BlockingScheduler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / '.env')

try:
    # import after adjusting sys.path
    from email_service import send_morning_report, send_evening_report
except Exception as exc:
    raise RuntimeError("Failed to import email_service; ensure project root is on PYTHONPATH") from exc

scheduler = BlockingScheduler()

# Morning report at 07:00
scheduler.add_job(send_morning_report, 'cron', hour=7, minute=0, id='morning_report')
# Evening report at 17:00
scheduler.add_job(send_evening_report, 'cron', hour=17, minute=0, id='evening_report')

if __name__ == '__main__':
    print('Starting email scheduler: morning at 07:00, evening at 17:00')
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print('Scheduler stopped')
