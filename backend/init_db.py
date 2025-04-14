# init_db.py
from backend.db import engine, Base
from backend.models import Function, ExecutionLog  # Import all your models

def init_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()