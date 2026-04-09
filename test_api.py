import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import the app, Base, and get_db from your project files
from fastAPI import app
from Proiectul import Base, get_db

# --- 1. CONFIGURARE BAZĂ DE DATE DE TEST (SQLite în memorie partajată) ---
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in the test database
Base.metadata.create_all(bind=engine)

# --- 2. SUPRASCRIERE DEPENDENȚĂ (Override) ---
# Tell the API to use the test database instead of the MSSQL server
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# --- 3. INIȚIALIZARE TEST CLIENT ---
client = TestClient(app)

# --- 4. CAZURI DE TEST ---

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Sistemul este activ."}

def test_create_identifier():
    response = client.post(
        "/identifiers/",
        json={
            "identifier_name": "ID_001",
            "description": "Test Identifier",
            "identifier_type": "Sensor"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["identifier_name"] == "ID_001"
    assert data["description"] == "Test Identifier"

def test_create_existing_identifier():
    # Try to create the same identifier again to test the error
    response = client.post(
        "/identifiers/",
        json={
            "identifier_name": "ID_001",
            "description": "Duplicate",
            "identifier_type": "Sensor"
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Identifier already exists"}

def test_get_identifiers():
    response = client.get("/identifiers/")
    assert response.status_code == 200
    data = response.json()
    # Should have at least the one created in the previous test
    assert len(data) >= 1
    assert data[0]["identifier_name"] == "ID_001"

def test_create_country():
    response = client.post(
        "/countries/",
        json={
            "name": "Romania",
            "iso_code": "RO",
            "short_code": "ROU"
        },
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Romania"

def test_create_consumer_unit():
    # ConsumerUnit has ForeignKey to Country, so the country created above must exist
    response = client.post(
        "/consumer-units/",
        json={
            "number_of_consumers": 100,
            "country_name": "Romania"  # Links to the country above
        },
    )
    assert response.status_code == 200
    assert response.json()["country_name"] == "Romania"