import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
passwd = os.getenv("DB_PASS")
database = os.getenv("DB_NAME")
encoded_passwd = quote_plus(passwd)

print(host, user, passwd, database)

SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{user}:{encoded_passwd}@{host}/{database}"

print(SQLALCHEMY_DATABASE_URL)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print("Database connected")
Base = declarative_base()  # This will now work without the warning
