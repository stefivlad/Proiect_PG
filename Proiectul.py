import pyodbc
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DECIMAL
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal
import warnings

# Suppress SQLAlchemy warning for unrecognized SQL Server version
warnings.filterwarnings("ignore", message="Unrecognized server version info")

# --- DATABASE SETUP ---
DATABASE_URL = (
    "mssql+pyodbc://@STEFANIAVLAD/PG_DevSchool"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
)

engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- SQLALCHEMY MODELS ---

class Identifiers(Base):
    __tablename__ = 'Identifiers'
    identifier_name = Column(String(255), primary_key=True)
    description = Column(Text, nullable=True)
    identifier_type = Column(String(255), nullable=True)

class Countries(Base):
    __tablename__ = 'countries'
    name = Column(String(200), primary_key=True)
    iso_code = Column(String(200), nullable=False)
    short_code = Column(String(200), nullable=True)

class ConsumerUnits(Base):
    __tablename__ = 'consumerunits'  # Fixed typo from 'cosumerunits'
    number_of_consumers = Column(Integer, primary_key=True)
    country_name = Column(String(255), ForeignKey('countries.name'), primary_key=True)

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

class Relationships(Base):
    __tablename__ = 'relationships'
    from_identifier_name = Column(String(255), ForeignKey('Identifiers.identifier_name'), primary_key=True)
    to_identifier_name = Column(String(255), ForeignKey('Identifiers.identifier_name'), primary_key=True)
    relationship_name = Column(String(255))

class Characteristics(Base):
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

class IdentifierCharacteristics(Base):
    __tablename__ = 'identifier_characteristics'
    identifier_name = Column(String(255), ForeignKey('Identifiers.identifier_name'), primary_key=True)
    master_name = Column(String(255), primary_key=True)
    characteristic_name = Column(String(255), primary_key=True)

# Create tables
Base.metadata.create_all(engine)

# --- PYDANTIC MODELS (SCHEMAS) ---

# Identifiers
class IdentifiersCreate(BaseModel):
    identifier_name: str
    description: Optional[str] = None
    identifier_type: Optional[str] = None

class IdentifiersResponse(IdentifiersCreate):
    model_config = ConfigDict(from_attributes=True)

class IdentifiersUpdate(BaseModel):
    description: Optional[str] = None
    identifier_type: Optional[str] = None

# Countries
class CountriesCreate(BaseModel):
    name: str
    iso_code: str  # Changed from Optional[str] = None to required str
    short_code: str

class CountriesResponse(CountriesCreate):
    model_config = ConfigDict(from_attributes=True)

class CountriesUpdate(BaseModel):
    name: Optional[str] = None
    iso_code: Optional[str] = None
    short_code: Optional[str] = None

# Ownership
class OwnershipCreate(BaseModel):
    identifier_name: str
    user_id_tnumber: str
    originator_first_name: Optional[str] = None
    originator_last_name: Optional[str] = None
    user_id_intranet: Optional[str] = None
    email: Optional[str] = None
    owner_first_name: Optional[str] = None
    owner_last_name: Optional[str] = None

class OwnershipResponse(OwnershipCreate):
    model_config = ConfigDict(from_attributes=True)

class OwnershipUpdate(BaseModel):
    originator_first_name: Optional[str] = None
    originator_last_name: Optional[str] = None
    user_id_intranet: Optional[str] = None
    email: Optional[str] = None
    owner_first_name: Optional[str] = None
    owner_last_name: Optional[str] = None

# Relationships
class RelationshipsCreate(BaseModel):
    from_identifier_name: str
    to_identifier_name: str
    relationship_name: str

class RelationshipsResponse(RelationshipsCreate):
    model_config = ConfigDict(from_attributes=True)

class RelationshipsUpdate(BaseModel):
    relationship_name: Optional[str] = None

# Characteristics
class CharacteristicsCreate(BaseModel):
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

class CharacteristicsResponse(CharacteristicsCreate):
    model_config = ConfigDict(from_attributes=True)

class CharacteristicsUpdate(BaseModel):
    specifics: Optional[str] = None
    action_required: Optional[str] = None
    report_type: Optional[str] = None
    data_type: Optional[str] = None
    lower_target: Optional[Decimal] = None
    target: Optional[Decimal] = None
    upper_target: Optional[Decimal] = None
    engineering_unit: Optional[str] = None

# IdentifierCharacteristics
class IdentifierCharacteristicsCreate(BaseModel):
    identifier_name: str
    master_name: str
    characteristic_name: str

class IdentifierCharacteristicsResponse(IdentifierCharacteristicsCreate):
    model_config = ConfigDict(from_attributes=True)

class IdentifierCharacteristicsUpdate(BaseModel):
    identifier_name: Optional[str] = None
    master_name: Optional[str] = None
    characteristic_name: Optional[str] = None

# ConsumerUnits
class ConsumerUnitsCreate(BaseModel):
    number_of_consumers: int
    country_name: str

class ConsumerUnitsResponse(ConsumerUnitsCreate):
    model_config = ConfigDict(from_attributes=True)

class ConsumerUnitsUpdate(BaseModel):
    number_of_consumers: Optional[int] = None
    country_name: Optional[str] = None