from ..crud.store_crud import create_store, get_store_by_id, get_stores_by_owner_id
from sqlmodel import Session
from ..models import StoreCreate, User, Store
from fastapi import HTTPException, status


def create_store_service(session: Session, store: StoreCreate, current_user: User):
  return create_store(session=session, store=store, owner_id=current_user.id)

def get_store_detail(
    session: Session,
    store_id: int,
    current_user: User
)-> Store | None:
  store = get_store_by_id(session=session, store_id=store_id)

  if not store:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Stores not found"
    )

  if store.owner_id != current_user.id:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Not authorized to access this store"
    )

  return store

def get_my_stores(session: Session, current_user: User) -> list[Store]:
  return get_stores_by_owner_id(session=session, owner_id=current_user.id)