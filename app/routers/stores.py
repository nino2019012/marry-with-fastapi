from fastapi import APIRouter, Depends
from ..models import StorePublic, StoreCreate, User
from ..db import SessionDep
from ..services.store_service import create_store_service
from typing import Annotated
from app.security import get_current_active_user
from app.services.store_service import get_store_detail, get_my_stores, create_store_service

router = APIRouter(
  prefix="/stores",
  tags=["stores"],
)

# 가게 만들기(수정 필요)
@router.post("", response_model=StorePublic)
def create_store(
  store: StoreCreate,
  session: SessionDep,
  current_user: Annotated[User, Depends(get_current_active_user)]
  ) -> StorePublic:
  return create_store_service(session=session, store=store, current_user=current_user)

#해당 사용자의 가게 모두 조회
@router.get("", response_model=list[StorePublic])
def read_stores(
  session: SessionDep,
  current_user: Annotated[User, Depends(get_current_active_user)]
):
  return get_my_stores(session=session, current_user=current_user)

#특정 가게 조회
@router.get("/{store_id}", response_model=StorePublic)
def get_store_by_id(
  store_id: int,
  session: SessionDep,
  current_user: Annotated[User, Depends(get_current_active_user)]                                                               
)-> StorePublic:
  return get_store_detail(session=session, store_id=store_id, current_user= current_user)
