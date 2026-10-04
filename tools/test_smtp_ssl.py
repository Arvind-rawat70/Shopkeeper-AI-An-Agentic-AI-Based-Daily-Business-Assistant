import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import smtplib

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / '.env')

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT_SSL', '465'))
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

print('HOST:', EMAIL_HOST)
print('PORT:', EMAIL_PORT)
print('SENDER SET:', bool(EMAIL_SENDER))
print('PASSWORD SET:', bool(EMAIL_PASSWORD))

try:
    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, timeout=30) as s:
        s.set_debuglevel(1)
        s.login(EMAIL_SENDER, EMAIL_PASSWORD)
    print('SMTP SSL auth: OK')
except Exception as e:
    print('SMTP SSL auth: FAILED')
    print(repr(e))
    raise
