import pyodbc
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DECIMAL
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from decimal import Decimal

# --- 1. CONFIGURARE BAZA DE DATE ---
DATABASE_URL = (
    "mssql+pyodbc://@STEFANIAVLAD/PG_DevSchool"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 2. MODELE SQLALCHEMY (Tabelele din baza de date) ---

class Identifier(Base):
    __tablename__ = 'Identifiers'
    identifier_name = Column(String(255), primary_key=True)
    description = Column(Text, nullable=True)
    identifier_type = Column(String(255), nullable=True)

class Country(Base):
    __tablename__ = 'countries'
    name = Column(String(200), primary_key=True)
    iso_code = Column(String(200), nullable=False)
    short_code = Column(String(200), nullable=True)

class ConsumerUnit(Base):
    __tablename__ = 'consumerunits' # Am corectat typo-ul din cosumerunits
    number_of_consumers = Column(Integer, primary_key=True)
    country_name = Column(String(200), ForeignKey('countries.name'), primary_key=True)

class Ownership(Base):
    __tablename__ = 'Ownership'
    identifier_name = Column(String(255), ForeignKey('Identifiers.identifier_name'), primary_key=True)
    user_id_tnumber = Column(String(255), primary_key=True)
    originator_first_name = Column(String(255))
    originator_last_name = Column(String(255))
    user_id_intranet = Column(String(255))
    email = Column(String(255))
    owner_first_name = Column(String(255))
    owner_last_name = Column(String(255))

class Relationship(Base):
    __tablename__ = 'relationships'
    from_identifier_name = Column(String(255), ForeignKey('Identifiers.identifier_name'), primary_key=True)
    to_identifier_name = Column(String(255), ForeignKey('Identifiers.identifier_name'), primary_key=True)
    relationship_name = Column(String(255))

class Characteristic(Base):
    __tablename__ = 'characteristics'
    master_name = Column(String(255), primary_key=True)
    name = Column(String(255), primary_key=True)
    specifics = Column(String(255))
    action_required = Column(String(255))
    report_type = Column(String(255))
    data_type = Column(String(255))
    lower_target = Column(DECIMAL(10, 2))
    target = Column(DECIMAL(10, 2))
    upper_target = Column(DECIMAL(10, 2))
    engineering_unit = Column(String(255))

class IdentifierCharacteristic(Base):
    __tablename__ = 'identifier_characteristics'
    identifier_name = Column(String(255), ForeignKey('Identifiers.identifier_name'), primary_key=True)
    master_name = Column(String(255), primary_key=True)
    characteristic_name = Column(String(255), primary_key=True)

# Creăm tabelele în baza de date
Base.metadata.create_all(engine)

# --- 3. MODELE PYDANTIC (Scheme validare API) ---

class IdentifierBase(BaseModel):
    identifier_name: str
    description: Optional[str] = None
    identifier_type: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class CountryBase(BaseModel):
    name: str
    iso_code: str
    short_code: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ConsumerUnitBase(BaseModel):
    number_of_consumers: int
    country_name: str
    model_config = ConfigDict(from_attributes=True)

class OwnershipBase(BaseModel):
    identifier_name: str
    user_id_tnumber: str
    originator_first_name: Optional[str] = None
    originator_last_name: Optional[str] = None
    user_id_intranet: Optional[str] = None
    email: Optional[str] = None
    owner_first_name: Optional[str] = None
    owner_last_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class RelationshipBase(BaseModel):
    from_identifier_name: str
    to_identifier_name: str
    relationship_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class CharacteristicBase(BaseModel):
    master_name: str
    name: str
    specifics: Optional[str] = None
    action_required: Optional[str] = None
    report_type: Optional[str] = None
    data_type: Optional[str] = None
    lower_target: Optional[Decimal] = None
    target: Optional[Decimal] = None
    upper_target: Optional[Decimal] = None
    engineering_unit: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class IdentifierCharacteristicBase(BaseModel):
    identifier_name: str
    master_name: str
    characteristic_name: str
    model_config = ConfigDict(from_attributes=True)


# --- 4. RUTE API (ENDPOINTS) ---
app = FastAPI(title="ProiectPy Factory API")

@app.get("/")
def root():
    return {"message": "API-ul complet funcționează conectat la MARIA/proiectpy!"}

# --- IDENTIFIERS ---
@app.post("/identifiers/", response_model=IdentifierBase)
def create_identifier(identifier: IdentifierBase, db: Session = Depends(get_db)):
    if db.query(Identifier).filter(Identifier.identifier_name == identifier.identifier_name).first():
        raise HTTPException(status_code=400, detail="Identifier already exists")
    new_item = Identifier(**identifier.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get("/identifiers/", response_model=List[IdentifierBase])
def get_identifiers(db: Session = Depends(get_db)):
    return db.query(Identifier).all()

# --- COUNTRIES ---
@app.post("/countries/", response_model=CountryBase)
def create_country(country: CountryBase, db: Session = Depends(get_db)):
    if db.query(Country).filter(Country.name == country.name).first():
        raise HTTPException(status_code=400, detail="Country already exists")
    new_item = Country(**country.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get("/countries/", response_model=List[CountryBase])
def get_countries(db: Session = Depends(get_db)):
    return db.query(Country).all()

# --- CONSUMER UNITS ---
@app.post("/consumer-units/", response_model=ConsumerUnitBase)
def create_consumer_unit(item: ConsumerUnitBase, db: Session = Depends(get_db)):
    if db.query(ConsumerUnit).filter(ConsumerUnit.number_of_consumers == item.number_of_consumers, 
                                     ConsumerUnit.country_name == item.country_name).first():
        raise HTTPException(status_code=400, detail="ConsumerUnit already exists")
    new_item = ConsumerUnit(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get("/consumer-units/", response_model=List[ConsumerUnitBase])
def get_consumer_units(db: Session = Depends(get_db)):
    return db.query(ConsumerUnit).all()

# --- OWNERSHIP ---
@app.post("/ownership/", response_model=OwnershipBase)
def create_ownership(item: OwnershipBase, db: Session = Depends(get_db)):
    if db.query(Ownership).filter(Ownership.identifier_name == item.identifier_name, 
                                  Ownership.user_id_tnumber == item.user_id_tnumber).first():
        raise HTTPException(status_code=400, detail="Ownership already exists")
    new_item = Ownership(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get("/ownership/", response_model=List[OwnershipBase])
def get_ownership(db: Session = Depends(get_db)):
    return db.query(Ownership).all()

# --- RELATIONSHIPS ---
@app.post("/relationships/", response_model=RelationshipBase)
def create_relationship(item: RelationshipBase, db: Session = Depends(get_db)):
    if db.query(Relationship).filter(Relationship.from_identifier_name == item.from_identifier_name, 
                                     Relationship.to_identifier_name == item.to_identifier_name).first():
        raise HTTPException(status_code=400, detail="Relationship already exists")
    new_item = Relationship(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get("/relationships/", response_model=List[RelationshipBase])
def get_relationships(db: Session = Depends(get_db)):
    return db.query(Relationship).all()

# --- CHARACTERISTICS ---
@app.post("/characteristics/", response_model=CharacteristicBase)
def create_characteristic(item: CharacteristicBase, db: Session = Depends(get_db)):
    if db.query(Characteristic).filter(Characteristic.master_name == item.master_name, 
                                       Characteristic.name == item.name).first():
        raise HTTPException(status_code=400, detail="Characteristic already exists")
    new_item = Characteristic(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get("/characteristics/", response_model=List[CharacteristicBase])
def get_characteristics(db: Session = Depends(get_db)):
    return db.query(Characteristic).all()

# --- IDENTIFIER CHARACTERISTICS ---
@app.post("/identifier-characteristics/", response_model=IdentifierCharacteristicBase)
def create_identifier_characteristic(item: IdentifierCharacteristicBase, db: Session = Depends(get_db)):
    if db.query(IdentifierCharacteristic).filter(IdentifierCharacteristic.identifier_name == item.identifier_name,
                                                 IdentifierCharacteristic.master_name == item.master_name,
                                                 IdentifierCharacteristic.characteristic_name == item.characteristic_name).first():
        raise HTTPException(status_code=400, detail="IdentifierCharacteristic already exists")
    new_item = IdentifierCharacteristic(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get("/identifier-characteristics/", response_model=List[IdentifierCharacteristicBase])
def get_identifier_characteristics(db: Session = Depends(get_db)):
    return db.query(IdentifierCharacteristic).all()








import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importăm aplicația, baza și funcția de dependență din fișierul tău principal
# Presupunem că fișierul tău se numește `main.py`
from main import app, Base, get_db

# --- 1. CONFIGURARE BAZĂ DE DATE DE TEST (SQLite în memorie) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creăm tabelele în baza de date temporară
Base.metadata.create_all(bind=engine)

# --- 2. SUPRASCRIERE DEPENDENȚĂ (Override) ---
# Spunem API-ului să folosească baza de date de test în loc de serverul MARIA
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
    assert response.json() == {"message": "API-ul complet funcționează conectat la MARIA/proiectpy!"}

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
    # Încercăm să creăm același identifier din nou pentru a testa eroarea
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
    # Trebuie să avem cel puțin elementul creat la testul anterior
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
    # ConsumerUnit are ForeignKey către Country, deci trebuie să existe țara creată mai sus
    response = client.post(
        "/consumer-units/",
        json={
            "number_of_consumers": 100,
            "country_name": "Romania" # Se leagă de țara de mai sus
        },
    )
    assert response.status_code == 200
    assert response.json()["country_name"] == "Romania"