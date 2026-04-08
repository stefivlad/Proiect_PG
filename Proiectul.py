import pyodbc

# Connect to SQL Server using Windows Authentication (SSMS)
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=STEFANIAVLAD;'       # ex: localhost\SQLEXPRESS
    'DATABASE=PG_DevSchool;'                
    'Trusted_Connection=yes;'        # Windows Authentication
)

cursor = conn.cursor() # ca un mouse care ma ajuta sa ma plimb prin baza de date


from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# Define the SQL Server LocalDB database
# Server: (localdb)\localhost  |  Database: fastapi_db  |  Windows Authentication
DATABASE_URL = (
    "mssql+pyodbc://@STEFANIAVLAD/PG_DevSchool"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
)

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a base class for declarative models
Base = declarative_base()

# Define a Product model (table)
class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    price = Column(Integer, nullable=False)

# Create all tables in the database
Base.metadata.create_all(engine)

# Create a new session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from pydantic import BaseModel
from typing import Optional

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: int

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: int

    class Config:
        from_attributes = True  # Enables compatibility with SQLAlchemy models

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None


    