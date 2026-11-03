from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from contextlib import asynccontextmanager
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from pydantic import BaseModel
from datetime import timedelta, datetime, timezone
import jwt
from sqlmodel import select
from sqlalchemy.orm import selectinload
from fastapi.staticfiles import StaticFiles

from .db import *
from .models import *
from .security import *

from .routers import users, token, stores

@asynccontextmanager
async def lifespan(app: FastAPI):
  create_db_and_tables()
  yield

app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(token.router)
app.include_router(stores.router)

'''
@app.get("/users")
def get_users(session: SessionDep) -> list[UserPublic]:
  users = session.exec(select(User)).all()
  return users

@app.get("/users/{user_id}")
def get_user(session: SessionDep, user_id: int) -> UserPublic:
  user_db = session.get(User, user_id)
  return user_db

@app.get("/", response_class=HTMLResponse)
def get_login_page(request: Request):
  return templates.TemplateResponse(
    request=request,
    name="login.html"
  )


@app.post("/token")
async def login_for_access_token(
  form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
  session: SessionDep):
  # db 데이터와 form 데이터 비교후 user 객체 가져옴
  user = authenticate_user(form_data.username, form_data.password, session)
  if not user:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Incorrect username or password",
      headers={"WWW-Authenticate": "Bearer"},
      )
  access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  access_token = create_access_token(
    data={"sub": user.phone_number}, expires_delta=access_token_expires
  )
  response = RedirectResponse(url="/stores", status_code=status.HTTP_303_SEE_OTHER)
  response.set_cookie(
    key="access_token",
    value=f"Bearer {access_token}",
    httponly=True,
    samesite="lax"
  )
  return response

@app.get("/stores", response_class=HTMLResponse)
async def read_stores(
  request: Request,
  session: SessionDep,
  current_user: Annotated[User, Depends(get_current_active_user)]
):
  stores = session.exec(select(Store).where(Store.owner_id == current_user.id)).all()

  return templates.TemplateResponse(
    request=request,
    name="stores.html",
    context={"stores": stores, "user": current_user}
  )

@app.get("/stores/{store_id}/contracts", response_class=HTMLResponse)
def read_contracts(
  request: Request,
  store_id: int,
  current_user: Annotated[User, Depends(get_current_active_user)],
  session: SessionDep
):
  store = session.get(Store, store_id)
  if not store:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")

  if store.owner_id != current_user.id:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")

  contracts = session.exec(
    select(Contract).where(Contract.store_id == store.id)
    .options(selectinload(Contract.work_logs))
    .options(selectinload(Contract.worker))).all()

  contracts_with_logs = [c for c in contracts if c.work_logs]
  contracts_without_logs = [c for c in contracts if not c.work_logs]

  return templates.TemplateResponse(
    request=request,
    name="contracts.html",
    context={
      "contracts_with_logs": contracts_with_logs,
      "contracts_without_logs": contracts_without_logs,
      "store": store,
      "current_user": current_user,
    }
  )
'''