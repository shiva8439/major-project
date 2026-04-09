from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from pathlib import Path
import os

# Config
SQLITE_URL = "sqlite:///./app.db"
BACKEND_DIR = Path(__file__).parent.parent

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    image_type = Column(String, nullable=False)  # 'chest_xray' or 'brain_mri'
    prediction = Column(String, nullable=False)  # 'Normal' or 'Pneumonia'/'Tumor'
    confidence = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    original_image_path = Column(String)
    heatmap_path = Column(String)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create DB file dir if not exists
BACKEND_DIR.mkdir(exist_ok=True)
Path(BACKEND_DIR, "app.db").touch(exist_ok=True)
