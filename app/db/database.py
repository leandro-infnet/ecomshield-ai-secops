import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import make_url
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.models import User

load_dotenv()


def get_engine():
    url = os.getenv("DATABASE_URL", "sqlite:///./data/processed/ecomshield.db")
    parsed = make_url(url)
    database_path = parsed.database
    if parsed.get_backend_name() == "sqlite" and database_path is not None and database_path != ":memory:":
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    return create_engine(url, connect_args={"check_same_thread": False} if url.startswith("sqlite:") else {})


engine = get_engine()


def init_db():
    SQLModel.metadata.create_all(engine)
    username = os.getenv("BOOTSTRAP_USERNAME")
    password = os.getenv("BOOTSTRAP_PASSWORD")
    if bool(username) != bool(password):
        raise RuntimeError("BOOTSTRAP_USERNAME e BOOTSTRAP_PASSWORD devem ser definidos juntos")
    if username and password:
        from app.core.security import hash_password
        with Session(engine) as session:
            if session.exec(select(User).where(User.username == username)).first() is None:
                session.add(User(username=username, password_hash=hash_password(password)))
                session.commit()


def get_session():
    with Session(engine) as session:
        yield session
