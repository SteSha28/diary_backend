from jwt import encode
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from fastapi import Depends
from datetime import datetime, timedelta, timezone



SECRET_KEY = "coWNCIONJND834ni942b4u8b484v495h58MIIEpAIBAAKCAQEAwhvqCC+37A+"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_jwt_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)