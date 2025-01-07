from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jwt import encode, decode
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from fastapi import Depends

SECRET_KEY = "coWNCIONJND834ni942b4u8b484v495h58MIIEpAIBAAKCAQEAwhvqCC+37A+"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_jwt_token(data: dict):
    return encode(data, SECRET_KEY, algorithm=ALGORITHM)

