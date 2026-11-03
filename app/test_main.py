from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
import pytest

from .models import User, Store
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
   
'''
def test_login_wrong_password(session: Session, client: TestClient):
   user = User(
      name="이승욱",
      phone_number=phone_number_plain,
      password=get_password_hash(password_plain),
      role="OWNER"
   )
   session.add(user)
   session.commit()

   response = client.post("/token", data={
      "username": phone_number_plain, "password": "wrong_password"}
      )

   assert response.status_code == 401
   assert response.json()["detail"] == "Incorrect username or password"
   assert response.headers["WWW-Authenticate"] == "Bearer"

def test_access_protected_route_with_cookie(session: Session, client: TestClient):
   password_plain="6940"
   user = User(
      name="이승욱",
      phone_number="01086057662",
      password=get_password_hash(password_plain),
      role="OWNER",
   )
   session.add(user)
   session.commit()

   login_data = {"username": "01086057662", "password": "6940"}
   login_response = client.post("/token", data=login_data, follow_redirects=False)
   assert login_response.status_code == 303

   response = client.get("/stores")
   assert response.status_code == 200

def test_access_protected_route_without_cookie(client: TestClient, session: Session):
   response = client.get("/stores")
   assert response.status_code == 401




# /stores/{store_id}/contracts

def test_read_contracts_success(session: Session, client: TestClient):
   plain_password = "6940"
   owner = User(
         name="이승욱",
         phone_number="01086057662",
         password=get_password_hash(plain_password),
         role="OWNER"
      )
   session.add(owner)
   session.commit()
   session.refresh(owner)

   store = Store(name="스타벅스 충효점", owner_id=owner.id)
   session.add(store)
   session.commit()
   session.refresh(store)

   def override_get_current_active_user():
      return owner

   app.dependency_overrides[get_current_active_user] = override_get_current_active_user

   response = client.get(f"/stores/{store.id}/contracts")
   assert response.status_code == 200


def test_read_contracts_store_not_found(session: Session, client: TestClient):
   plain_password = "6940"
   owner = User(
          name="이승욱",
          phone_number="01086057662",
          password=get_password_hash(plain_password),
          role="OWNER"
     )
   
   def override():
      return User()
   
   app.dependency_overrides[get_current_active_user] = override

   response = client.get("/stores/99999/contracts")
   assert response.status_code == 404
   assert response.json()["detail"] == "Store not found"


def test_read_contracts_forbidden(session: Session, client: TestClient):
   plain_password = "6940"
   owner = User(
          name="이승욱",
          phone_number="01086057662",
          password=get_password_hash(plain_password),
          role="OWNER"
     )
   other_user = User(
          name="다른사람",
          phone_number="01012345678",
          password=get_password_hash("1234"),
          role="OWNER"
    )

   session.add_all([owner, other_user])
   session.commit()
   session.refresh(owner)
   session.refresh(other_user)

   store = Store(
      name="스타벅스 충효점",
      owner_id=other_user.id
   )
   session.add(store)
   session.commit()
   session.refresh(store)

   def override_get_current_user():
      return owner

   app.dependency_overrides[get_current_active_user] = override_get_current_user

   response = client.get(f"/stores/{store.id}/contracts")
   assert response.status_code == 403

'''