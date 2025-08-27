from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime, timedelta
from uuid import UUID

from app.db.session import get_db
from app.models.appointment import Appointment
from app.models.schedule_optimization import ScheduleOptimization
from app.core.auth import get_current_user
from ml.optimizer import ScheduleOptimizer
from ml.predictor import NoShowPredictor

router = APIRouter()


@router.post("/optimize-schedule")
async def optimize_schedule(
    optimization_date: date,
    provider_id: Optional[UUID] = None,
    strategy: str = Query("balanced", regex="^(conservative|balanced|aggressive)$"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Generate optimized schedule for a specific date
    """
    # Get appointments for the date
    query = db.query(Appointment).filter(
        Appointment.scheduled_time >= optimization_date,
        Appointment.scheduled_time < optimization_date + timedelta(days=1)
    )
    
    if provider_id:
        query = query.filter(Appointment.provider_id == provider_id)
    
    appointments = query.all()
    
    if not appointments:
        raise HTTPException(status_code=404, detail="No appointments found for optimization")
    
    # Get no-show predictions
    predictor = NoShowPredictor()
    no_show_predictions = {}
    
    for appointment in appointments:
        appointment_data = {
            'scheduled_time': appointment.scheduled_time,
            'patient_id': appointment.patient_id,
            'provider_id': appointment.provider_id,
            'appointment_type': appointment.appointment_type,
            'duration_minutes': appointment.duration_minutes,
            'patient_no_show_rate': 0.15,  # Would come from patient history
            'patient_total_appointments': 10,
            'practice_no_show_rate': 0.12
        }
        
        no_show_prob, _ = predictor.predict(appointment_data)
        no_show_predictions[str(appointment.id)] = no_show_prob
    
    # Create optimizer with practice settings
    practice_settings = {
        'max_overbook_percentage': 0.15,
        'min_no_show_threshold': 0.10,
        'buffer_time_minutes': 5,
        'strategy': strategy
    }
    
    optimizer = ScheduleOptimizer(practice_settings)
    
    # Convert appointments to dict format
    appointments_dict = [
        {
            'id': str(appointment.id),
            'provider_id': str(appointment.provider_id),
            'patient_id': str(appointment.patient_id),
            'scheduled_time': appointment.scheduled_time,
            'duration_minutes': appointment.duration_minutes,
            'appointment_type': appointment.appointment_type.value
        }
        for appointment in appointments
    ]
    
    # Get provider schedules (simplified for demo)
    provider_schedules = {
        str(provider_id): {
            'start': '09:00',
            'end': '17:00',
            'slot_duration': 30
        }
    }
    
    # Run optimization
    result = optimizer.optimize_daily_schedule(
        appointments_dict,
        no_show_predictions,
        provider_schedules
    )
    
    # Save optimization to database
    db_optimization = ScheduleOptimization(
        practice_id=current_user.practice_id,
        provider_id=provider_id,
        optimization_date=optimization_date,
        optimization_type='daily',
        original_schedule=result.original_schedule,
        optimized_schedule=result.optimized_schedule,
        changes_made=result.changes,
        predicted_revenue_gain=result.predicted_revenue_gain,
        optimization_score=result.optimization_score,
        model_version='1.0.0',
        model_confidence=0.85
    )
    
    db.add(db_optimization)
    db.commit()
    
    return {
        'optimization_id': db_optimization.id,
        'optimization_date': optimization_date,
        'original_schedule': result.original_schedule,
        'optimized_schedule': result.optimized_schedule,
        'changes': result.changes,
        'predicted_revenue_gain': result.predicted_revenue_gain,
        'optimization_score': result.optimization_score,
        'recommendations': result.recommendations
    }


@router.post("/apply-optimization/{optimization_id}")
async def apply_optimization(
    optimization_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Apply a generated optimization to the actual schedule
    """
    optimization = db.query(ScheduleOptimization).filter(
        ScheduleOptimization.id == optimization_id
    ).first()
    
    if not optimization:
        raise HTTPException(status_code=404, detail="Optimization not found")
    
    if optimization.is_applied:
        raise HTTPException(status_code=400, detail="Optimization already applied")
    
    # Apply changes (simplified - in production would update actual appointments)
    optimization.is_applied = 1
    optimization.applied_at = datetime.utcnow()
    optimization.applied_by = current_user.email
    
    db.commit()
    
    return {
        'message': 'Optimization applied successfully',
        'applied_changes': len(optimization.changes_made)
    }


@router.get("/recommendations")
async def get_schedule_recommendations(
    target_date: date = Query(default=date.today()),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get real-time schedule recommendations
    """
    # Get today's appointments
    appointments = db.query(Appointment).filter(
        Appointment.scheduled_time >= target_date,
        Appointment.scheduled_time < target_date + timedelta(days=1),
        Appointment.practice_id == current_user.practice_id
    ).all()
    
    recommendations = []
    
    # Check for high-risk appointments
    high_risk_count = sum(1 for apt in appointments if apt.no_show_probability > 0.4)
    if high_risk_count > 0:
        recommendations.append({
            'type': 'high_risk_alert',
            'priority': 'high',
            'message': f'{high_risk_count} appointments have high no-show risk',
            'action': 'Send additional reminders or consider overbooking'
        })
    
    # Check for optimization opportunities
    total_appointments = len(appointments)
    if total_appointments > 0:
        avg_no_show_prob = sum(apt.no_show_probability for apt in appointments) / total_appointments
        if avg_no_show_prob > 0.15:
            recommendations.append({
                'type': 'optimization_opportunity',
                'priority': 'medium',
                'message': f'Average no-show probability is {avg_no_show_prob:.1%}',
                'action': 'Consider running schedule optimization'
            })
    
    # Check for empty slots
    # (Simplified - would check against provider schedules in production)
    if total_appointments < 20:  # Assuming 20 is typical daily capacity
        recommendations.append({
            'type': 'capacity_alert',
            'priority': 'low',
            'message': f'Only {total_appointments} appointments scheduled',
            'action': 'Open slots for same-day bookings or promote availability'
        })
    
    return recommendations


@router.post("/suggest-reschedule")
async def suggest_reschedule_times(
    appointment_id: UUID,
    preferred_days_ahead: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Suggest optimal reschedule times for an appointment
    """
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Get available slots (simplified)
    suggestions = []
    current_date = date.today()
    
    for days_ahead in range(1, preferred_days_ahead + 1):
        target_date = current_date + timedelta(days=days_ahead)
        
        # Skip weekends
        if target_date.weekday() in [5, 6]:
            continue
        
        # Suggest morning and afternoon slots
        for hour in [9, 10, 11, 14, 15, 16]:
            suggested_time = datetime.combine(target_date, datetime.min.time().replace(hour=hour))
            
            # Check if slot is available (simplified)
            existing = db.query(Appointment).filter(
                Appointment.provider_id == appointment.provider_id,
                Appointment.scheduled_time == suggested_time
            ).first()
            
            if not existing:
                suggestions.append({
                    'suggested_time': suggested_time.isoformat(),
                    'provider_id': appointment.provider_id,
                    'confidence_score': 0.9 - (days_ahead * 0.02)  # Prefer sooner appointments
                })
        
        # Return top 5 suggestions
        if len(suggestions) >= 5:
            break
    
    return suggestions[:5]