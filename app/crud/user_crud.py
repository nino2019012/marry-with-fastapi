from sqlmodel import Session, select
from ..models import User, UserCreate

def create_db_user(session: Session, user: UserCreate, hashed_password: str) -> User:
  db_user = User(
    name= user.name,
    phone_number=user.phone_number,
    password=hashed_password,
    role=user.role,
  )
  session.add(db_user)
  session.commit()
  session.refresh(db_user)
  return db_user

def get_user_by_phone_number(session: Session, phone_number: str) -> User | None:
  statement = select(User).where(phone_number == phone_number)
  return session.exec(statement=statement).first()