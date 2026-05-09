import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite:///./test_gsgi.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_token(client):
    client.post("/api/auth/register", json={
        "username": "angel", "email": "angel@gsgi.com",
        "password": "gsgi2024!", "role": "admin"
    })
    resp = client.post("/api/auth/token", data={
        "username": "angel", "password": "gsgi2024!"
    })
    return resp.json()["access_token"]


@pytest.fixture
def auth(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def sample_employee(client, auth):
    resp = client.post("/api/employees", json={
        "first_name": "John", "last_name": "Smith",
        "email": "john@gsgi.com", "license_type": "D",
        "pay_rate": 18.50
    }, headers=auth)
    return resp.json()


@pytest.fixture
def sample_site(client, auth):
    resp = client.post("/api/sites", json={
        "name": "Bridgewater Bay", "client_name": "Bridgewater Bay POA",
        "city": "Naples", "billing_rate": 25.0
    }, headers=auth)
    return resp.json()
