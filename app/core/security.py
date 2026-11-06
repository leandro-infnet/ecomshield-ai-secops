import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.db.database import get_session
from app.db.models import User

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
ALGORITHM = "HS256"


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    username: str


def secret_key():
    value = os.getenv("SECRET_KEY", "")
    if len(value) < 32:
        raise RuntimeError("SECRET_KEY deve ter ao menos 32 caracteres")
    return value


def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 600_000)
    return f"{salt}${digest.hex()}"


def verify_password(password, stored):
    try:
        salt, _ = stored.split("$", 1)
        return hmac.compare_digest(hash_password(password, salt), stored)
    except (ValueError, TypeError):
        return False


def create_access_token(subject):
    minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    if minutes <= 0:
        raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES deve ser positivo")
    return jwt.encode({"sub": subject, "exp": datetime.now(timezone.utc) + timedelta(minutes=minutes)}, secret_key(), algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> AuthenticatedUser:
    unauthorized = HTTPException(status_code=401, detail="Credenciais inválidas", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, secret_key(), algorithms=[ALGORITHM], options={"require": ["sub", "exp"]})
        subject = payload["sub"]
        if not isinstance(subject, str) or not subject:
            raise unauthorized
    except jwt.InvalidTokenError:
        raise unauthorized from None
    user = session.exec(select(User).where(User.username == subject)).first()
    if user is None or user.id is None:
        raise unauthorized
    return AuthenticatedUser(id=user.id, username=user.username)
