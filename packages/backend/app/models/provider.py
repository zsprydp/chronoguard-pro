from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class Provider(Base):
    __tablename__ = "providers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    
    # Basic Info
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    specialty = Column(String(100))
    license_number = Column(String(50))
    
    # Scheduling Preferences
    avg_appointment_duration = Column(Integer, default=30)
    buffer_time_minutes = Column(Integer, default=5)
    max_daily_appointments = Column(Integer, default=20)
    
    # Working Hours (JSON format: {"monday": {"start": "09:00", "end": "17:00"}, ...})
    working_hours = Column(JSON, default={})
    break_times = Column(JSON, default={})
    
    # Performance Metrics
    total_appointments = Column(Integer, default=0)
    no_show_count = Column(Integer, default=0)
    cancellation_count = Column(Integer, default=0)
    avg_patient_satisfaction = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    practice = relationship("Practice", backref="providers")
    appointments = relationship("Appointment", back_populates="provider")