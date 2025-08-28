from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from werkzeug.security import generate_password_hash, check_password_hash
from app.db.base import Base


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


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic Info
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    
    # Role & Permissions
    role = Column(Enum(UserRole), default=UserRole.PRACTICE_OWNER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Practice Association
    practice_id = Column(UUID(as_uuid=True), nullable=True)  # Will link to practice
    
    # Subscription Info
    subscription_status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL)
    stripe_customer_id = Column(String(100))
    subscription_id = Column(String(100))
    current_period_end = Column(DateTime(timezone=True))
    
    # Trial Info
    trial_start = Column(DateTime(timezone=True), server_default=func.now())
    trial_end = Column(DateTime(timezone=True))
    trial_used = Column(Boolean, default=False)
    
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
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_trial_expired(self) -> bool:
        """Check if trial period has expired"""
        if not self.trial_end:
            return False
        return self.trial_end < func.now()
    
    def get_full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def can_access_feature(self, feature: str) -> bool:
        """Check if user can access specific feature based on subscription"""
        if self.subscription_status == SubscriptionStatus.ACTIVE:
            return True
        if self.subscription_status == SubscriptionStatus.TRIAL and not self.is_trial_expired():
            return True
        return False