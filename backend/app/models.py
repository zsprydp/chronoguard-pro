from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime, timedelta
import enum
import uuid
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    PRACTICE_OWNER = "practice_owner"
    PRACTICE_ADMIN = "practice_admin"
    STAFF_MEMBER = "staff_member"
    PROVIDER = "provider"

class SubscriptionStatus(str, enum.Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    SUSPENDED = "suspended"

class SubscriptionPlan(str, enum.Enum):
    TRIAL = "trial"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    CANCELLED = "cancelled"

# Practice Model
class Practice(Base):
    __tablename__ = "practices"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    timezone = Column(String(50), default="UTC")
    
    # Subscription
    subscription_plan = Column(SQLEnum(SubscriptionPlan), default=SubscriptionPlan.TRIAL)
    subscription_status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.TRIAL)
    stripe_customer_id = Column(String(100))
    subscription_id = Column(String(100))
    current_period_end = Column(DateTime(timezone=True))
    
    # Limits based on plan
    max_providers = Column(Integer, default=2)
    max_appointments_per_month = Column(Integer, default=100)
    
    # Usage tracking
    appointments_this_month = Column(Integer, default=0)
    total_revenue_saved = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="practice")
    providers = relationship("Provider", back_populates="practice")
    patients = relationship("Patient", back_populates="practice")
    appointments = relationship("Appointment", back_populates="practice")

# User Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    
    # Role & Permissions
    role = Column(SQLEnum(UserRole), default=UserRole.PRACTICE_OWNER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Practice Association
    practice_id = Column(String(36), ForeignKey("practices.id"))
    
    # Trial Info
    trial_start = Column(DateTime(timezone=True), server_default=func.now())
    trial_end = Column(DateTime(timezone=True))
    
    # Usage Tracking
    last_login = Column(DateTime(timezone=True))
    login_count = Column(Integer, default=0)
    
    # Authentication
    email_verification_token = Column(String(100))
    password_reset_token = Column(String(100))
    password_reset_expires = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    practice = relationship("Practice", back_populates="users")
    
    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)
    
    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

# Provider Model
class Provider(Base):
    __tablename__ = "providers"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    practice_id = Column(String(36), ForeignKey("practices.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    specialty = Column(String(100))
    
    # Schedule Settings
    avg_appointment_duration = Column(Integer, default=30)
    buffer_time_minutes = Column(Integer, default=5)
    max_daily_appointments = Column(Integer, default=20)
    
    # Performance Metrics
    total_appointments = Column(Integer, default=0)
    no_show_count = Column(Integer, default=0)
    no_show_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    practice = relationship("Practice", back_populates="providers")
    appointments = relationship("Appointment", back_populates="provider")

# Patient Model
class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    practice_id = Column(String(36), ForeignKey("practices.id"), nullable=False)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255))
    phone = Column(String(20), nullable=False)
    date_of_birth = Column(DateTime)
    
    # Insurance Information
    insurance_provider = Column(String(100))
    insurance_id = Column(String(50))
    
    # Risk Factors
    no_show_count = Column(Integer, default=0)
    cancellation_count = Column(Integer, default=0)
    total_appointments = Column(Integer, default=0)
    no_show_rate = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    practice = relationship("Practice", back_populates="patients")
    appointments = relationship("Appointment", back_populates="patient")
    
    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

# Appointment Model
class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    practice_id = Column(String(36), ForeignKey("practices.id"), nullable=False)
    provider_id = Column(String(36), ForeignKey("providers.id"), nullable=False)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)
    
    # Scheduling Details
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=30)
    appointment_type = Column(String(50))
    
    # Status
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    confirmed_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    
    # AI Predictions
    no_show_probability = Column(Float, default=0.0)
    risk_level = Column(String(20))
    prediction_confidence = Column(Float)
    
    # Financial
    service_cost = Column(Float, default=0.0)
    
    # Notes
    reason_for_visit = Column(Text)
    provider_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    practice = relationship("Practice", back_populates="appointments")
    provider = relationship("Provider", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")