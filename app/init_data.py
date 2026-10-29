from sqlmodel import Session, select
from app.db import create_db_and_tables, engine
from app.models import *
from app.security import get_password_hash
from datetime import datetime
from contextlib import contextmanager

def init_data():
  with Session(engine) as session:
      existing_user = session.exec(select(User)).first()
      if not existing_user:
        owner1 = User(
          name="이승욱",
          phone_number="01086057662",
          password=get_password_hash("6940"),
          role=UserRole.OWNER
        )
        owner2 = User(
          name="김사장",
          phone_number="01012345678",
          password=get_password_hash("1234"),
          role=UserRole.OWNER
        )

        #-- 아르바이트생
        worker1 = User(
          name="최민지",
          phone_number="01012345670",
          password=get_password_hash("12345"),
          role=UserRole.WORKER,
        )
        worker2 = User(
          name="정다은",
          phone_number="01012345671",
          password=get_password_hash("123456"),
          role=UserRole.WORKER,
        )

        session.add_all([owner1, owner2, worker1, worker2])
        session.commit()

        #-- 가게
        store1 = Store(
          name="이승욱 편의점1",
          is_5_or_more_employee=True,
          owner_id=owner1.id,
        )

        store2 = Store(
                  name="이승욱 편의점2",
                  is_5_or_more_employee=False,
                  owner_id=owner1.id,
                )
        store3 = Store(
                  name="이승욱 편의점3",
                  is_5_or_more_employee=True,
                  owner_id=owner1.id,
                )
        store4 = Store(
          name="김사장 카페",
          is_5_or_more_employee=False,
          owner_id=owner2.id,
        )

        session.add_all([store1, store2, store3, store4])
        session.commit()

        #----- 계약서 ----
        contract1 = Contract(
           hourly_wage=10000,
           store_id=1,
           worker_id=3,
        )
        contract2 = Contract(
           hourly_wage=10000,
           store_id=1,
           worker_id=4,
        )

        session.add_all([contract1, contract2])
        session.commit()

        #----- Work_logs ------
        work_log1 = Work_log(
           contract_id=1,
           check_in=datetime(2026, 10, 8, 9, 0, 0, tzinfo=UTC),
           check_out=datetime(2026, 10, 9, 18, 0, 0, tzinfo=UTC),
        )
        work_log2 = Work_log(
          contract_id=1,
          check_in=datetime(2026, 10, 9, 9, 0, 0, tzinfo=UTC),
          check_out=datetime(2026, 10, 9, 18, 0, 0, tzinfo=UTC),
        )

        session.add_all([work_log1, work_log2])
        session.commit()

if __name__ == "__main__":
   create_db_and_tables()
   init_data()