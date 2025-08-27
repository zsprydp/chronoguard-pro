from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID

from app.db.session import get_db
from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentWithPrediction
)
from app.services.appointment_service import AppointmentService
from app.core.auth import get_current_user
from ml.predictor import NoShowPredictor

router = APIRouter()
appointment_service = AppointmentService()
predictor = NoShowPredictor()


@router.get("/", response_model=List[AppointmentResponse])
async def get_appointments(
    date: Optional[date] = Query(None),
    provider_id: Optional[UUID] = Query(None),
    patient_id: Optional[UUID] = Query(None),
    status: Optional[AppointmentStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retrieve appointments with optional filters
    """
    query = db.query(Appointment)
    
    if date:
        query = query.filter(Appointment.scheduled_time >= date)
        query = query.filter(Appointment.scheduled_time < date + timedelta(days=1))
    
    if provider_id:
        query = query.filter(Appointment.provider_id == provider_id)
    
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    
    if status:
        query = query.filter(Appointment.status == status)
    
    appointments = query.offset(skip).limit(limit).all()
    
    return appointments


@router.post("/", response_model=AppointmentWithPrediction)
async def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new appointment with no-show prediction
    """
    # Create appointment in database
    db_appointment = appointment_service.create_appointment(db, appointment)
    
    # Get no-show prediction
    appointment_data = {
        'scheduled_time': appointment.scheduled_time,
        'patient_id': appointment.patient_id,
        'provider_id': appointment.provider_id,
        'appointment_type': appointment.appointment_type,
        'duration_minutes': appointment.duration_minutes,
        # Add patient history (would come from database in production)
        'patient_no_show_rate': 0.15,
        'patient_total_appointments': 10,
        'practice_no_show_rate': 0.12
    }
    
    no_show_prob, prediction_details = predictor.predict(appointment_data)
    
    # Update appointment with prediction
    db_appointment.no_show_probability = no_show_prob
    db_appointment.risk_level = prediction_details['risk_level']
    db_appointment.prediction_factors = prediction_details
    db.commit()
    
    return AppointmentWithPrediction(
        **db_appointment.__dict__,
        prediction=prediction_details
    )


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: UUID,
    appointment_update: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update an existing appointment
    """
    db_appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Update fields
    for field, value in appointment_update.dict(exclude_unset=True).items():
        setattr(db_appointment, field, value)
    
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment


@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: UUID,
    reason: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Cancel an appointment
    """
    db_appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    db_appointment.status = AppointmentStatus.CANCELLED
    db_appointment.cancelled_at = datetime.utcnow()
    
    if reason:
        db_appointment.patient_notes = reason
    
    db.commit()
    
    return {"message": "Appointment cancelled successfully"}


@router.post("/{appointment_id}/confirm")
async def confirm_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Confirm an appointment
    """
    db_appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    db_appointment.status = AppointmentStatus.CONFIRMED
    db_appointment.confirmed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Appointment confirmed successfully"}


@router.post("/batch-predict")
async def batch_predict_no_shows(
    appointment_ids: List[UUID],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get no-show predictions for multiple appointments
    """
    appointments = db.query(Appointment).filter(
        Appointment.id.in_(appointment_ids)
    ).all()
    
    predictions = []
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
        
        no_show_prob, prediction_details = predictor.predict(appointment_data)
        
        predictions.append({
            'appointment_id': appointment.id,
            'no_show_probability': no_show_prob,
            'risk_level': prediction_details['risk_level'],
            'top_factors': prediction_details['top_factors']
        })
    
    return predictions