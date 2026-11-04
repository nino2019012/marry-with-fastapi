from datetime import datetime, UTC
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from sqlalchemy import Column, DateTime


# ----- User -----

class UserRole(str, Enum):
  OWNER = "OWNER"
  WORKER = "WORKER"

class UserBase(SQLModel):
  name: str

class User(UserBase, table=True):
  id: int | None = Field(default=None, primary_key=True)
  phone_number: str = Field(index=True)
  password: str
  role: UserRole
  disabled: bool = Field(default=False)

  stores: list["Store"] = Relationship(back_populates="user")
  contracts: list["Contract"] = Relationship(back_populates="worker")

class UserPublic(UserBase):
  id: int

class UserCreate(UserBase):
  phone_number: str
  password: str
  role: UserRole

#----- Store -----

class StoreBase(SQLModel):
  name: str = Field(index=True)

class Store(StoreBase, table=True):
  id: int | None = Field(default=None, primary_key=True)
  is_5_or_more_employees: bool = Field(default=False)
  owner_id: int = Field(foreign_key="user.id")

  user: User = Relationship(back_populates="stores")
  contracts: list["Contract"] = Relationship(back_populates="store")

class StorePublic(StoreBase):
  id: int
  is_5_or_more_employees: bool
  owner_id: int

class StoreCreate(StoreBase):
  #owner_id: int => store를 만들 때 토큰에서 user_id를 넣음
  is_5_or_more_employees: bool

class StoreUpdate(SQLModel):
  name: str | None = None
  is_5_or_more_employees: bool | None = None

# ------ Contract ------

class ContractBase(SQLModel):
  created_at: datetime = Field(
    default_factory=lambda: datetime.now(UTC),
    sa_column=Column(DateTime(timezone=True)))

class Contract(ContractBase, table=True):
  id: int | None = Field(default=None, primary_key=True)
  hourly_wage: int

  store_id: int = Field(foreign_key="store.id")
  worker_id: int = Field(foreign_key="user.id")

  store: Store = Relationship(back_populates="contracts")
  worker: User = Relationship(back_populates="contracts")

  work_logs: list["Work_log"] = Relationship(back_populates="contract")

class ContractPublic(ContractBase):
  id: int
  store_id: int
  worker_id: int

class ContractCreate(ContractBase):
  hourly_wage: int
  #store_id는 경로에서 가져오기
  worker_id: int

class ContractUpdate(SQLModel):
  hourly_wage: int | None = None

# --------- Work_logs

class Work_logBase(SQLModel):
  check_in: datetime = Field(
    sa_column=Column(DateTime(timezone=True))
  )
  check_out: datetime = Field(
    sa_column=Column(DateTime(timezone=True))
  )

class Work_log(Work_logBase, table=True):
  id: int | None = Field(default=None, primary_key=True)
  contract_id: int = Field(foreign_key="contract.id")

  contract: Contract = Relationship(back_populates="work_logs")

class Work_logPublic(Work_logBase):
  id: int
  contract_id: int

class Work_logCreate(Work_logBase):
  pass

class Work_logUpdate(SQLModel):
  check_in: datetime | None = None
  check_out: datetime | None = None
