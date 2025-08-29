from sqlalchemy import Column, String, DateTime, Integer, Float, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base import Base


class IndustryType(str, enum.Enum):
    FAMILY_MEDICINE = "family_medicine"
    DERMATOLOGY = "dermatology"
    DENTISTRY = "dentistry"
    ORTHOPEDICS = "orthopedics"
    CARDIOLOGY = "cardiology"
    PEDIATRICS = "pediatrics"
    PSYCHIATRY = "psychiatry"
    OPTOMETRY = "optometry"
    PHYSICAL_THERAPY = "physical_therapy"
    VETERINARY = "veterinary"
    BEAUTY_SPA = "beauty_spa"
    PROFESSIONAL_SERVICES = "professional_services"


class SubscriptionTier(str, enum.Enum):
    TRIAL = "trial"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Practice(Base):
    __tablename__ = "practices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    industry = Column(Enum(IndustryType), nullable=False)
    timezone = Column(String(50), default="UTC")
    
    # Business Details
    address = Column(String(500))
    phone = Column(String(20))
    email = Column(String(255))
    website = Column(String(255))
    
    # Subscription Info
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.TRIAL)
    subscription_start = Column(DateTime(timezone=True))
    subscription_end = Column(DateTime(timezone=True))
    
    # Settings
    max_overbook_percentage = Column(Float, default=0.15)
    min_no_show_threshold = Column(Float, default=0.10)
    auto_optimize_enabled = Column(Integer, default=1)
    reminder_settings = Column(JSON, default={})
    
    # Analytics
    total_appointments = Column(Integer, default=0)
    total_no_shows = Column(Integer, default=0)
    revenue_saved = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())