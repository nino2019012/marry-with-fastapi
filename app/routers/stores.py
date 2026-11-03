from fastapi import APIRouter
from ..models import StorePublic, StoreCreate, Store
from ..db import SessionDep
from ..services.store_service import create_store_service

router = APIRouter(
  prefix="/stores",
  tags=["stores"],
)

@router.post("", response_model=StorePublic)
def create_store(store: StoreCreate, session: SessionDep) -> StorePublic:
  return create_store_service(session=session, store=store)