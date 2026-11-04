from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.db import SessionDep
from app.services.auth_service import authenticate_user, create_user_token

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(
  prefix="/token",
  tags=["token"],
)

#로그인
@router.post("")
def login_for_access_token(
  form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
  session: SessionDep
):
  user = authenticate_user(session=session, username=form_data.username, password=form_data.password)
  if not user:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Incorrect username or password",
      headers={"WWW-Authenticate": "Bearer"},
    )

  access_token = create_user_token(user)

  return {
    "access_token": access_token,
    "token_type": "bearer",
  }