import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base, get_db
from app.database.models import User
from app.main import app
from app.services.auth_service import hash_password, verify_password

# Use an isolated in-memory database with StaticPool for authentication testing
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)

    # Seed test users with securely hashed passwords
    db = TestingSessionLocal()
    inspector_user = User(
        username="test_inspector",
        hashed_password=hash_password("inspector_pass_123"),
        role="INSPECTOR",
        full_name="Insp. Test Officer",
        organization="Legal Metrology Department",
    )
    manufacturer_user = User(
        username="test_manufacturer",
        hashed_password=hash_password("manufacturer_pass_456"),
        role="MANUFACTURER",
        full_name="Test Quality Manager",
        organization="Apex Foods Pvt Ltd",
    )
    db.add(inspector_user)
    db.add(manufacturer_user)
    db.commit()
    db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


def test_password_hashing_and_verification():
    raw_pass = "SuperSecret#2026"
    hashed = hash_password(raw_pass)

    # Plaintext must not be present in the hashed output
    assert raw_pass not in hashed
    assert "$" in hashed

    # Verification must succeed for exact password
    assert verify_password(raw_pass, hashed) is True

    # Verification must fail for incorrect password
    assert verify_password("WrongPassword", hashed) is False
    assert verify_password("", hashed) is False
    assert verify_password(raw_pass, "invalid$salt$hash") is False


def test_login_inspector_success():
    client = TestClient(app)
    response = client.post(
        "/api/auth/login",
        json={"username": "test_inspector", "password": "inspector_pass_123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_inspector"
    assert data["role"] == "INSPECTOR"
    assert data["full_name"] == "Insp. Test Officer"
    assert data["organization"] == "Legal Metrology Department"
    assert "id" in data

    # Plaintext and hashed passwords must NEVER be present in the response
    assert "password" not in data
    assert "hashed_password" not in data


def test_login_manufacturer_success():
    client = TestClient(app)
    response = client.post(
        "/api/auth/login",
        json={"username": "test_manufacturer", "password": "manufacturer_pass_456"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_manufacturer"
    assert data["role"] == "MANUFACTURER"
    assert data["full_name"] == "Test Quality Manager"
    assert data["organization"] == "Apex Foods Pvt Ltd"


def test_login_invalid_password_returns_401():
    client = TestClient(app)
    response = client.post(
        "/api/auth/login",
        json={"username": "test_inspector", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_login_nonexistent_user_returns_401():
    client = TestClient(app)
    response = client.post(
        "/api/auth/login",
        json={"username": "nonexistent_user_999", "password": "some_password"},
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_seed_users_idempotence():
    from app.database.seed_users import seed_users

    db = TestingSessionLocal()
    try:
        # Call seed_users first time
        users1 = seed_users(db)
        assert len(users1) == 2

        # Check that inspector and manufacturer exist
        inspector = db.query(User).filter(User.username == "inspector").first()
        assert inspector is not None
        assert inspector.role == "INSPECTOR"
        assert inspector.full_name == "Insp. Vikram Singh"
        assert inspector.organization == "Legal Metrology Department, Govt of India"
        assert "inspector123" not in inspector.hashed_password

        manufacturer = db.query(User).filter(User.username == "manufacturer").first()
        assert manufacturer is not None
        assert manufacturer.role == "MANUFACTURER"
        assert manufacturer.full_name == "Sunil Sharma (Quality Assurance)"
        assert manufacturer.organization == "Britannia Industries Ltd"
        assert "manufacturer123" not in manufacturer.hashed_password

        # Call seed_users second time (idempotency check)
        users2 = seed_users(db)
        assert len(users2) == 2

        # Total inspector count and manufacturer count must still be 1
        inspector_count = db.query(User).filter(User.username == "inspector").count()
        assert inspector_count == 1

        manufacturer_count = db.query(User).filter(User.username == "manufacturer").count()
        assert manufacturer_count == 1
    finally:
        db.close()


def test_demo_users_login():
    client = TestClient(app)

    # Login with demo inspector
    resp_insp = client.post(
        "/api/auth/login",
        json={"username": "inspector", "password": "inspector123"},
    )
    assert resp_insp.status_code == 200
    insp_data = resp_insp.json()
    assert insp_data["username"] == "inspector"
    assert insp_data["role"] == "INSPECTOR"
    assert insp_data["full_name"] == "Insp. Vikram Singh"

    # Login with demo manufacturer
    resp_mfr = client.post(
        "/api/auth/login",
        json={"username": "manufacturer", "password": "manufacturer123"},
    )
    assert resp_mfr.status_code == 200
    mfr_data = resp_mfr.json()
    assert mfr_data["username"] == "manufacturer"
    assert mfr_data["role"] == "MANUFACTURER"
    assert mfr_data["full_name"] == "Sunil Sharma (Quality Assurance)"

