from sqlmodel import Session
from ..models import StoreCreate, Store

def create_db_store(session: Session, store: StoreCreate) -> Store:
  db_store = Store(
    name=store.name,
    is_5_or_more_employees=store.is_5_or_more_employees,
    owner_id=store.owner_id,
  )

  session.add(db_store)
  session.commit()
  session.refresh(db_store)

  return db_store