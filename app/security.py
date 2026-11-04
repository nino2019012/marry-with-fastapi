from pwdlib import PasswordHash
from sqlmodel import select
from datetime import timedelta, timezone
from pydantic import BaseModel
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Annotated
from fastapi import Depends, Cookie, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .db import SessionDep
from .models import *

ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = "4af9e36cdb2b72594205a3955f878f263a53229bc95307696babcfc63a16f7bb"
ALGORITHM = "HS256"

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")

class Token(BaseModel):
  access_token: str
  token_type: str

class TokenData(BaseModel):
  username: str | None = None

def verify_password(plain_password, hased_password):
  return password_hash.verify(plain_password, hased_password)

def get_password_hash(password):
  return password_hash.hash(password)

def get_user(username: str, session: SessionDep):
  user = session.exec(select(User).where(User.phone_number == username)).first()
  if user:
    return user

def authenticate_user(
    username: str,
    password: str,
    session: SessionDep,
    ):
  user = get_user(username, session)
  if not user:
    verify_password(password, DUMMY_HASH)
    return False
  if not verify_password(password, user.password):
    return False
  return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.now(timezone.utc) + expires_delta
  else:
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

async def get_current_user(
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)]
):
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}
  )

  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")
    if username is None:
      raise credentials_exception
    token_data = TokenData(username=username)
  except InvalidTokenError:
    raise credentials_exception

  user = get_user(username=token_data.username, session=session)
  if user is None:
    raise credentials_exception
  return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
  if current_user.disabled:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
  return current_user