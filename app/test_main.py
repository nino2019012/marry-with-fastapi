from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
import pytest

from .models import User, Store, UserRole
from .main import app
from .db import get_session
from .security import verify_password, get_password_hash, get_current_active_user

password_plain = "1234"
phone_number_plain = "01012345678"


@pytest.fixture(name="session")
def session_fixture():
  engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
  )
  SQLModel.metadata.create_all(engine)
  with Session(engine) as session:
    yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
       return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# /users
def test_create_user(session: Session, client: TestClient):
   payload = {
      "name":"이승욱",
      "phone_number": phone_number_plain,
      "password":password_plain,
      "role":"OWNER",
      }

   response = client.post("/users", json=payload)

   assert response.status_code == 200
   data = response.json()
   created_id = data["id"]

   assert data["name"] == payload["name"]
   assert data["id"] is not None

   assert "password" not in data

   db_user = session.get(User, created_id)

   assert db_user is not None
   assert db_user.password != payload["password"]
   assert verify_password(payload["password"], db_user.password)

# /token
def test_login_for_access_token(session: Session, client: TestClient):
   user = User(
         name="이승욱",
         phone_number=phone_number_plain,
         password=get_password_hash(password_plain),
         role="OWNER",
   )
   session.add(user)
   session.commit()

   login_data = {
      "username": phone_number_plain,
      "password": password_plain,
   }

   response = client.post("/token", data=login_data)

   assert response.status_code == 200

   data = response.json()
   assert "access_token" in data
   assert data["token_type"] == "bearer"
   assert data["access_token"] is not None

# get stores
def test_read_store_with_token(session: Session, client: TestClient):
   user = User(
         name="이승욱",
         phone_number=phone_number_plain,
         password=get_password_hash(password_plain),
         role=UserRole.OWNER,
      )
   session.add(user)
   session.commit()

   store = Store(
      name="스타벅스 충효점",
      is_5_or_more_employees=False,
      owner_id=user.id
   )
   session.add(store)
   session.commit()

   login_response = client.post(
      "/token",
      data={
         "username": phone_number_plain,
         "password": password_plain,
      }
    )

   token = login_response.json()["access_token"]
   headers = {"Authorization": f"Bearer {token}"}

   response = client.get(f"/stores/{store.id}", headers=headers)
   assert response.status_code == 200

# token을 통한 가게들 보이기
def test_read_stores_with_tokens(session: Session, client: TestClient):
   user = User(
      name="이승욱",
      phone_number=phone_number_plain,
      password=get_password_hash(password_plain),
      role=UserRole.OWNER,
   )
   other_user = User(
      name="다른 사장",
      phone_number="01099998888",
      password=get_password_hash(password_plain),
      role=UserRole.OWNER,
   )
   session.add_all([user, other_user])
   session.commit()

   store1 = Store(name="스타벅스 충효점", is_5_or_more_employees=False, owner_id=user.id)
   store2 = Store(name="스타벅스 터미널점", is_5_or_more_employees=True, owner_id=user.id)

   other_store = Store(name="투썸플레이스", is_5_or_more_employees=False, owner_id=other_user.id)

   session.add_all([store1, store2, other_store])
   session.commit()

   login_response = client.post(
      "/token",
      data={
         "username": phone_number_plain,
         "password": password_plain
      }
   )
   token = login_response.json()["access_token"]
   headers = {"Authorization": f"Bearer {token}"}

   response = client.get("/stores", headers=headers)

   assert response.status_code == 200
   data = response.json()
   assert data[0]["name"] == "스타벅스 충효점"
   assert data[1]["name"] == "스타벅스 터미널점"

def test_create_store_with_token(session: Session, client: TestClient):
  user = User(
      name="이승욱",
      phone_number=phone_number_plain,
      password=get_password_hash(password_plain),
      role=UserRole.OWNER,
  )
  session.add(user)
  session.commit()

  login_response = client.post(
     "/token",
     data={
        "username": phone_number_plain,
        "password": password_plain,
     }
  )
  token = login_response.json()["access_token"]
  headers = {"Authorization": f"Bearer {token}"}

  response = client.post(
     "/stores",
     json={
        "name":"스타벅스 보문점",
        "is_5_or_more_employees": True
     },
     headers=headers
  )

  assert response.status_code == 200
  data = response.json()
  assert data["name"] == "스타벅스 보문점"
  assert data["owner_id"] == user.id