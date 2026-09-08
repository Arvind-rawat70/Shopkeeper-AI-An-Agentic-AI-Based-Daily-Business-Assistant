from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

load_dotenv()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

missing = [k for k in ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME")
           if not os.getenv(k)]

if missing:
    raise EnvironmentError(
        f"Missing environment variables: {', '.join(missing)}"
    )

db_password_quoted = quote_plus(db_password)

database_url = (
    f"mysql+pymysql://{db_user}:{db_password_quoted}"
    f"@{db_host}/{db_name}"
)

engine = create_engine(database_url, pool_pre_ping=True)


# Test the connection
try:
    with engine.connect() as connection:
        print("Database connection successful!")
except Exception as e:
    print(f"Database connection failed: {e}")


# Read products
print("\nProducts:")
with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM products"))

    for row in result:
        print(row)