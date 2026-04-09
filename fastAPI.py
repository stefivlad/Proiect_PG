from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from Proiectul import (
    get_db, 
    Identifiers, IdentifiersCreate, IdentifiersResponse, IdentifiersUpdate,
    Countries, CountriesCreate, CountriesResponse, CountriesUpdate,
    Ownership, OwnershipCreate, OwnershipResponse, OwnershipUpdate,
    Relationships, RelationshipsCreate, RelationshipsResponse, RelationshipsUpdate,
    Characteristics, CharacteristicsCreate, CharacteristicsResponse, CharacteristicsUpdate,
    IdentifierCharacteristics, IdentifierCharacteristicsCreate, 
    IdentifierCharacteristicsResponse, IdentifierCharacteristicsUpdate,
    ConsumerUnits, ConsumerUnitsCreate, ConsumerUnitsResponse
)

app = FastAPI(title="PG DevSchool API")

@app.get('/')
async def root():
    return {'message': 'Sistemul este activ.'}

# --- 1. IDENTIFIERS ---
@app.post("/identifiers/", response_model=IdentifiersResponse)
def create_identifier(identifier: IdentifiersCreate, db: Session = Depends(get_db)):
    db_id = Identifiers(**identifier.model_dump())
    try:
        db.add(db_id)
        db.commit()
        db.refresh(db_id)
        return db_id
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Identifier already exists")

@app.get("/identifiers/", response_model=List[IdentifiersResponse])
def read_identifiers(db: Session = Depends(get_db)):
    return db.query(Identifiers).all()

@app.patch("/identifiers/{identifier_name}", response_model=IdentifiersResponse)
def update_identifier(identifier_name: str, update_data: IdentifiersUpdate, db: Session = Depends(get_db)):
    db_id = db.query(Identifiers).filter(Identifiers.identifier_name == identifier_name).first()
    if not db_id:
        raise HTTPException(status_code=404, detail="Identifier not found")
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(db_id, key, value)
    db.commit()
    db.refresh(db_id)
    return db_id

@app.delete("/identifiers/{identifier_name}")
def delete_identifier(identifier_name: str, db: Session = Depends(get_db)):
    db_id = db.query(Identifiers).filter(Identifiers.identifier_name == identifier_name).first()
    if not db_id: raise HTTPException(status_code=404, detail="Not found")
    db.delete(db_id)
    db.commit()
    return {"detail": "Deleted"}

# --- 2. COUNTRIES ---
@app.post("/countries/", response_model=CountriesResponse)
def create_country(country: CountriesCreate, db: Session = Depends(get_db)):
    db_country = Countries(**country.model_dump())
    try:
        db.add(db_country)
        db.commit()
        db.refresh(db_country)
        return db_country
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Country already exists")

@app.get("/countries/", response_model=List[CountriesResponse])
def read_countries(db: Session = Depends(get_db)):
    return db.query(Countries).all()

# --- 3. CONSUMER UNITS ---
@app.post("/consumer-units/", response_model=ConsumerUnitsResponse)
def create_consumer_unit(unit: ConsumerUnitsCreate, db: Session = Depends(get_db)):
    db_unit = ConsumerUnits(**unit.model_dump())
    try:
        db.add(db_unit)
        db.commit()
        db.refresh(db_unit)
        return db_unit
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Consumer unit already exists")

@app.get("/consumer-units/", response_model=List[ConsumerUnitsResponse])
def read_consumer_units(db: Session = Depends(get_db)):
    return db.query(ConsumerUnits).all()

# --- 4. OWNERSHIP ---
@app.post("/ownership/", response_model=OwnershipResponse)
def create_ownership(ownership: OwnershipCreate, db: Session = Depends(get_db)):
    db_own = Ownership(**ownership.model_dump())
    db.add(db_own)
    db.commit()
    db.refresh(db_own)
    return db_own

@app.get("/ownership/", response_model=List[OwnershipResponse])
def read_ownerships(db: Session = Depends(get_db)):
    return db.query(Ownership).all()

# --- 5. RELATIONSHIPS ---
@app.post("/relationships/", response_model=RelationshipsResponse)
def create_relationship(rel: RelationshipsCreate, db: Session = Depends(get_db)):
    db_rel = Relationships(**rel.model_dump())
    db.add(db_rel)
    db.commit()
    db.refresh(db_rel)
    return db_rel

@app.get("/relationships/", response_model=List[RelationshipsResponse])
def read_relationships(db: Session = Depends(get_db)):
    return db.query(Relationships).all()

# --- 6. CHARACTERISTICS ---
@app.post("/characteristics/", response_model=CharacteristicsResponse)
def create_characteristic(char: CharacteristicsCreate, db: Session = Depends(get_db)):
    db_char = Characteristics(**char.model_dump())
    db.add(db_char)
    db.commit()
    db.refresh(db_char)
    return db_char

@app.get("/characteristics/", response_model=List[CharacteristicsResponse])
def read_characteristics(db: Session = Depends(get_db)):
    return db.query(Characteristics).all()

# --- 7. IDENTIFIER CHARACTERISTICS ---
@app.post("/identifier-characteristics/", response_model=IdentifierCharacteristicsResponse)
def create_id_char_link(link: IdentifierCharacteristicsCreate, db: Session = Depends(get_db)):
    db_link = IdentifierCharacteristics(**link.model_dump())
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

@app.get("/identifier-characteristics/", response_model=List[IdentifierCharacteristicsResponse])
def read_id_char_links(db: Session = Depends(get_db)):
    return db.query(IdentifierCharacteristics).all()

@app.delete("/identifier-characteristics/{id_name}/{m_name}/{c_name}")
def delete_id_char_link(id_name: str, m_name: str, c_name: str, db: Session = Depends(get_db)):
    db_link = db.query(IdentifierCharacteristics).filter(
        IdentifierCharacteristics.identifier_name == id_name,
        IdentifierCharacteristics.master_name == m_name,
        IdentifierCharacteristics.characteristic_name == c_name
    ).first()
    if not db_link: raise HTTPException(status_code=404, detail="Link not found")
    db.delete(db_link)
    db.commit()
    return {"detail": "Link removed"}