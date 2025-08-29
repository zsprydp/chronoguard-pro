from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base import Base


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class AppointmentType(str, enum.Enum):
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    PROCEDURE = "procedure"
    CHECKUP = "checkup"
    EMERGENCY = "emergency"
    TELEHEALTH = "telehealth"


class BookingChannel(str, enum.Enum):
    PHONE = "phone"
    ONLINE = "online"
    WALK_IN = "walk_in"
    APP = "app"
    REFERRAL = "referral"


class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    
    # Scheduling Details
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=30)
    appointment_type = Column(Enum(AppointmentType), default=AppointmentType.CONSULTATION)
    
    # Status Tracking
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    confirmed_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    
    # Booking Information
    booking_channel = Column(Enum(BookingChannel), default=BookingChannel.PHONE)
    booked_at = Column(DateTime(timezone=True), server_default=func.now())
    booked_by = Column(String(255))  # Staff member or 'self' for online bookings
    
    # AI Predictions
    no_show_probability = Column(Float, default=0.0)  # 0.0 to 1.0
    risk_level = Column(String(20))  # low, medium, high
    prediction_factors = Column(JSON, default={})  # Detailed breakdown of risk factors
    prediction_timestamp = Column(DateTime(timezone=True))
    
    # Financial
    service_cost = Column(Float, default=0.0)
    insurance_coverage = Column(Float, default=0.0)
    copay_amount = Column(Float, default=0.0)
    
    # Communication
    reminders_sent = Column(JSON, default=[])  # List of reminder timestamps and methods
    confirmation_requested = Column(DateTime(timezone=True))
    confirmation_received = Column(DateTime(timezone=True))
    
    # Notes and Details
    reason_for_visit = Column(String(500))
    provider_notes = Column(String(1000))
    patient_notes = Column(String(500))
    
    # Optimization Flags
    is_overbooked = Column(Integer, default=0)  # Boolean flag
    is_buffer_slot = Column(Integer, default=0)  # Boolean flag
    optimization_score = Column(Float)  # How well this slot fits in the optimized schedule
    
    # Rescheduling History
    original_time = Column(DateTime(timezone=True))
    reschedule_count = Column(Integer, default=0)
    reschedule_history = Column(JSON, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    practice = relationship("Practice", backref="appointments")
    provider = relationship("Provider", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")