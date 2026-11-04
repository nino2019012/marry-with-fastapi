from fastapi import APIRouter
from sqlmodel import select

from ..db import *
from ..models import *
from ..security import *
from ..services.user_service import create_user_service

router = APIRouter(
  prefix="/users",
  tags=["users"],
)

#회원가입
@router.post("", response_model=UserPublic)
def create_user(user: UserCreate, session: SessionDep) -> UserPublic:
  return create_user_service(session=session, user=user)