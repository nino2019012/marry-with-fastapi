from ..crud.store_crud import create_db_store
from sqlmodel import Session
from ..models import StoreCreate


def create_store_service(session: Session, store: StoreCreate):
  return create_db_store(session=session, store=store)