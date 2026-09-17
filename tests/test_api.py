from datetime import datetime
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api import app
from src.database import Base, get_db
from src.decision import DecisionOutput
from src.models import User


TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def register_user(email: str, password: str = "password123"):
    response = client.post(
        "/register",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 201

    return response.json()


def login_user(email: str, password: str = "password123"):
    response = client.post(
        "/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def auth_headers(token: str):
    return {
        "Authorization": f"Bearer {token}"
    }


def test_register():
    response = client.post(
        "/register",
        json={
            "email": "alice@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201
    assert response.json()["email"] == "alice@example.com"


def test_duplicate_registration():
    register_user("alice@example.com")

    response = client.post(
        "/register",
        json={
            "email": "alice@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 409


def test_login():
    register_user("alice@example.com")

    response = client.post(
        "/login",
        json={
            "email": "alice@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_invalid_login():
    register_user("alice@example.com")

    response = client.post(
        "/login",
        json={
            "email": "alice@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


def test_get_me():
    register_user("alice@example.com")

    token = login_user("alice@example.com")

    response = client.get(
        "/me",
        headers=auth_headers(token)
    )

    assert response.status_code == 200
    assert response.json()["email"] == "alice@example.com"


def test_protected_endpoint_without_token():
    response = client.get("/tickets")

    assert response.status_code == 401


@patch(
    "src.api.make_decision"
)
def test_create_ticket_with_decision(mock_make_decision):

    mock_make_decision.return_value = DecisionOutput(
        action="REQUEST_PHOTOS",
        confidence=0.95,
        reason="Photos are required for damaged orders above ₹2,000.",
        sources=["damaged_goods.md"]
    )

    register_user("alice@example.com")

    token = login_user("alice@example.com")

    response = client.post(
        "/tickets",
        headers=auth_headers(token),
        json={
            "message": "My ₹3,500 order arrived damaged yesterday."
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["message"] == (
        "My ₹3,500 order arrived damaged yesterday."
    )

    assert data["decision"]["action"] == "REQUEST_PHOTOS"
    assert data["decision"]["confidence"] == 0.95
    assert data["decision"]["sources"] == [
        "damaged_goods.md"
    ]

    mock_make_decision.assert_called_once()


@patch(
    "src.api.make_decision"
)
def test_get_ticket_history(mock_make_decision):

    mock_make_decision.return_value = DecisionOutput(
        action="APPROVE_RETURN",
        confidence=0.98,
        reason="Unopened non-food product is eligible.",
        sources=["returns.md"]
    )

    register_user("alice@example.com")

    token = login_user("alice@example.com")

    client.post(
        "/tickets",
        headers=auth_headers(token),
        json={
            "message": "I want to return my unopened product."
        }
    )

    response = client.get(
        "/tickets",
        headers=auth_headers(token)
    )

    assert response.status_code == 200
    assert len(response.json()) == 1

    ticket = response.json()[0]

    assert ticket["decision"]["action"] == "APPROVE_RETURN"


@patch(
    "src.api.make_decision"
)
def test_user_cannot_access_another_users_ticket(
    mock_make_decision
):

    mock_make_decision.return_value = DecisionOutput(
        action="REQUEST_PHOTOS",
        confidence=0.95,
        reason="Photos required.",
        sources=["damaged_goods.md"]
    )

    register_user("alice@example.com")
    register_user("bob@example.com")

    alice_token = login_user("alice@example.com")
    bob_token = login_user("bob@example.com")

    response = client.post(
        "/tickets",
        headers=auth_headers(alice_token),
        json={
            "message": "My order arrived damaged."
        }
    )

    assert response.status_code == 201

    ticket_id = response.json()["id"]

    response = client.get(
        f"/tickets/{ticket_id}",
        headers=auth_headers(bob_token)
    )

    assert response.status_code == 404


def test_invalid_ticket_message():

    register_user("alice@example.com")

    token = login_user("alice@example.com")

    response = client.post(
        "/tickets",
        headers=auth_headers(token),
        json={
            "message": ""
        }
    )

    assert response.status_code == 422