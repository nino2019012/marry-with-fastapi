from datetime import timedelta
from sqlmodel import Session
from app.crud.user_crud import get_user_by_phone_number
from app.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

def authenticate_user(session: Session, username: str, password: str):
  user = get_user_by_phone_number(session=session, phone_number=username)
  if not user:
    return None
  if not verify_password(plain_password=password, hased_password=user.password):
    return None
  return user

def create_user_token(user) -> str:
  access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  return create_access_token(
    data={"sub": user.phone_number},
    expires_delta=access_token_expires,
  )