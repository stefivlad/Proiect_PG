from Proiectul import engine, Base
try:
    # Test connection
    with engine.connect() as conn:
        print("Database connection successful")
    # Create tables if not exist
    Base.metadata.create_all(engine)
    print("Tables created successfully")
except Exception as e:
    print(f"Error: {e}")