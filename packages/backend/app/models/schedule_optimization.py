from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON, DateTime, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class ScheduleOptimization(Base):
    __tablename__ = "schedule_optimizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"))
    
    # Optimization Details
    optimization_date = Column(Date, nullable=False)
    optimization_type = Column(String(50))  # daily, weekly, real_time
    
    # Schedule Data
    original_schedule = Column(JSON, nullable=False)  # Original appointment schedule
    optimized_schedule = Column(JSON, nullable=False)  # Optimized schedule with changes
    changes_made = Column(JSON, default=[])  # List of specific changes
    
    # Metrics
    predicted_no_shows = Column(Integer, default=0)
    recommended_overbooks = Column(Integer, default=0)
    slots_optimized = Column(Integer, default=0)
    
    # Financial Impact
    original_revenue = Column(Float, default=0.0)
    optimized_revenue = Column(Float, default=0.0)
    predicted_revenue_gain = Column(Float, default=0.0)
    actual_revenue_gain = Column(Float)  # Filled in after the day is complete
    
    # Performance Metrics
    optimization_score = Column(Float)  # Overall quality score of the optimization
    utilization_rate_before = Column(Float)  # % of time slots utilized
    utilization_rate_after = Column(Float)
    avg_wait_time_impact = Column(Float)  # Estimated impact on patient wait times
    
    # Application Status
    is_applied = Column(Integer, default=0)  # Boolean flag
    applied_at = Column(DateTime(timezone=True))
    applied_by = Column(String(255))  # User who approved the optimization
    
    # Feedback
    user_rating = Column(Integer)  # 1-5 star rating
    user_feedback = Column(String(500))
    
    # ML Model Info
    model_version = Column(String(50))
    model_confidence = Column(Float)  # Overall confidence in predictions
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    practice = relationship("Practice", backref="optimizations")