from sqlmodel import Session, select
from ..models import StoreCreate, Store

def create_store(session: Session, store: StoreCreate, owner_id: int) -> Store:
  db_store = Store.model_validate(store, update={"owner_id": owner_id})
  session.add(db_store)
  session.commit()
  session.refresh(db_store)
  return db_store

def get_store_by_id(session: Session, store_id: int) -> Store | None:
  return session.get(Store, store_id)

def get_stores_by_owner_id(session: Session, owner_id: int) -> list[Store]:
  statement = select(Store).where(Store.owner_id == owner_id)
  return session.exec(statement).all()
