from sqlmodel import Session
from ..models import User, UserCreate
from ..security import get_password_hash
from ..crud.user_crud import create_db_user

def create_user_service(session: Session, user: UserCreate) -> User:
  hashed_password = get_password_hash(user.password)
  return create_db_user(session=session, user=user, hashed_password=hashed_password)