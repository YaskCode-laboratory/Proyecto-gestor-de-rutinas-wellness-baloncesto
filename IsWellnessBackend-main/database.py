import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL .env no tiene un valor.")

is_sqlite = DATABASE_URL.startswith("sqlite")

connect_args = {}
if not is_sqlite:
    capath = "ca.pem"
    if os.path.exists(capath):
        connect_args["ssl"] = {"ca": capath}

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,
)

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()