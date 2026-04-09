import os
os.environ["TESTING"] = "1"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

# Import the app and dependency to override after TESTING is set
from fastAPI import app
from Proiectul import get_db, Identifiers, Countries, ConsumerUnits

# --- Dummy in-memory mock store for tests ---
class DummyQuery:
    def __init__(self, items, model, conditions=None):
        self.items = items
        self.model = model
        self.conditions = conditions or []

    def filter(self, *conditions):
        return DummyQuery(self.items, self.model, self.conditions + list(conditions))

    def all(self):
        results = list(self.items[self.model.__tablename__])
        for condition in self.conditions:
            results = [row for row in results if self._matches(row, condition)]
        return results

    def first(self):
        results = self.all()
        return results[0] if results else None

    def _matches(self, row, condition):
        try:
            column = condition.left.name
            value = condition.right.value
        except AttributeError:
            return False
        return getattr(row, column) == value

class DummyDB:
    def __init__(self):
        self.data = {
            "Identifiers": [],
            "countries": [],
            "consumerunits": [],
        }

    def query(self, model):
        return DummyQuery(self.data, model)

    def add(self, obj):
        table = obj.__tablename__
        if table == "Identifiers":
            if any(item.identifier_name == obj.identifier_name for item in self.data[table]):
                raise IntegrityError("duplicate", params=None, orig=None)
        self.data[table].append(obj)

    def commit(self):
        pass

    def rollback(self):
        pass

    def refresh(self, obj):
        pass

    def close(self):
        pass

# --- 2. SUPRASCRIERE DEPENDENȚĂ (Override) ---
# Use a shared dummy DB across test requests so created data persists between API calls
dummy_db = DummyDB()

def override_get_db():
    try:
        yield dummy_db
    finally:
        pass

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