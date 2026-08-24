from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

from security import hash_password

DATABASE_PATH = Path(__file__).resolve().parent / "interview.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def migrate_schema():
    """Apply the small schema updates needed by the current application."""
    columns = {column["name"] for column in inspect(engine).get_columns("users")}
    with engine.begin() as connection:
        if "password_hash" not in columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR"))

        if "password" in columns:
            legacy_users = connection.execute(
                text(
                    "SELECT id, password FROM users "
                    "WHERE password_hash IS NULL AND password IS NOT NULL"
                )
            ).fetchall()
            for user_id, legacy_password in legacy_users:
                connection.execute(
                    text(
                        "UPDATE users SET password_hash = :password_hash, password = NULL "
                        "WHERE id = :user_id"
                    ),
                    {
                        "password_hash": hash_password(legacy_password),
                        "user_id": user_id,
                    },
                )
            connection.execute(text("UPDATE users SET password = NULL WHERE password IS NOT NULL"))