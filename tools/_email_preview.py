import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so imports work when running as a script
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from email_service import build_daily_report

print("EMAIL_SENDER_SET", bool(os.getenv("EMAIL_SENDER")))
print("EMAIL_PASSWORD_SET", bool(os.getenv("EMAIL_PASSWORD")))
print("OWNER_EMAIL_SET", bool(os.getenv("OWNER_EMAIL")))
print("EMAIL_HOST", os.getenv("EMAIL_HOST", "smtp.gmail.com"))
print()
print("---EMAIL BODY PREVIEW---")
body = build_daily_report("morning")
print(body)
print("---END PREVIEW---")
