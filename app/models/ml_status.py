from sqlalchemy import Column, Integer, Boolean, DateTime, String
from datetime import datetime

from app.database.connection import Base

# Model untuk menyimpan status Machine Learning secara global di database
class MLStatus(Base):
    __tablename__ = "ml_status"

    id = Column(Integer, primary_key=True, index=True, default=1)
    needs_retrain = Column(Boolean, default=True)
    last_trained_at = Column(DateTime, nullable=True)
    last_dataset_update = Column(DateTime, default=datetime.utcnow)
    model_status = Column(String(50), default="OUTDATED") # OUTDATED atau READY
    model_version = Column(Integer, default=0)
