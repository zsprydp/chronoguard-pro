from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON, DateTime, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date)
    gender = Column(String(20))
    
    # Contact Information
    phone = Column(String(20), nullable=False)
    phone_secondary = Column(String(20))
    email = Column(String(255))
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    
    # Insurance Information
    insurance_provider = Column(String(100))
    insurance_plan = Column(String(100))
    insurance_id = Column(String(50))
    insurance_group = Column(String(50))
    
    # Communication Preferences
    preferred_contact_method = Column(String(20), default="phone")  # phone, email, sms
    reminder_preference = Column(JSON, default={})  # {"sms": true, "email": false, "hours_before": 24}
    language_preference = Column(String(20), default="en")
    
    # Risk Factors & History
    no_show_count = Column(Integer, default=0)
    cancellation_count = Column(Integer, default=0)
    total_appointments = Column(Integer, default=0)
    no_show_rate = Column(Float, default=0.0)
    avg_booking_lead_time = Column(Float)  # Average days between booking and appointment
    
    # ML Features
    risk_score = Column(Float, default=0.0)  # Current no-show risk score
    risk_factors = Column(JSON, default={})  # Detailed risk factor breakdown
    last_risk_calculation = Column(DateTime(timezone=True))
    
    # Patient Journey
    first_appointment = Column(DateTime(timezone=True))
    last_appointment = Column(DateTime(timezone=True))
    patient_since = Column(Date)
    
    # Additional Data
    notes = Column(String(1000))
    tags = Column(JSON, default=[])  # ["vip", "chronic_condition", etc.]
    custom_fields = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    practice = relationship("Practice", backref="patients")
    appointments = relationship("Appointment", back_populates="patient")