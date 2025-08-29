from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional, List
import jwt
import os
from dotenv import load_dotenv

# Import database stuff
from app.database import get_db, engine, Base
from app.models import User, Practice, Provider, Patient, Appointment, SubscriptionPlan, SubscriptionStatus, AppointmentStatus

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="ChronoGuard Pro - Database-Backed SaaS API",
    description="AI-Powered Appointment Optimization with Real Database",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7500", "http://localhost:7501", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "chronoguard-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
TRIAL_DAYS = int(os.getenv("TRIAL_DAYS", "14"))

# Pydantic Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    practice_name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    subscription_status: str
    trial_days_left: Optional[int] = None
    is_verified: bool
    practice_name: Optional[str] = None

    class Config:
        orm_mode = True

class PracticeResponse(BaseModel):
    id: str
    name: str
    subscription_plan: str
    subscription_status: str
    max_providers: int
    max_appointments_per_month: int
    appointments_this_month: int
    total_revenue_saved: float

    class Config:
        orm_mode = True

# Helper functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(db: Session = Depends(get_db), user_id: str = Depends(verify_token)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Authentication Endpoints
@app.post("/auth/register", response_model=dict)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create practice first
    practice = Practice(
        name=user_data.practice_name,
        subscription_plan=SubscriptionPlan.TRIAL,
        subscription_status=SubscriptionStatus.TRIAL,
        max_providers=2,
        max_appointments_per_month=100
    )
    db.add(practice)
    db.flush()  # Get the practice ID without committing
    
    # Create user
    user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        role="practice_owner",
        practice_id=practice.id,
        trial_end=datetime.utcnow() + timedelta(days=TRIAL_DAYS),
        is_verified=False
    )
    user.set_password(user_data.password)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(practice)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    # Calculate trial days
    trial_days_left = (user.trial_end - datetime.utcnow()).days if user.trial_end else TRIAL_DAYS
    
    return {
        "message": "Registration successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.value,
            "subscription_status": practice.subscription_status.value,
            "trial_days_left": trial_days_left,
            "is_verified": user.is_verified,
            "practice_name": practice.name
        }
    }

@app.post("/auth/login")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    # Find user
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not user.verify_password(login_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Update last login
    user.last_login = datetime.utcnow()
    user.login_count = (user.login_count or 0) + 1
    db.commit()
    
    # Get practice
    practice = user.practice
    
    # Calculate trial days left
    trial_days_left = None
    if user.trial_end:
        trial_days_left = max(0, (user.trial_end - datetime.utcnow()).days)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.value,
            "subscription_status": practice.subscription_status.value if practice else "trial",
            "trial_days_left": trial_days_left,
            "is_verified": user.is_verified,
            "practice_name": practice.name if practice else None
        }
    }

# Practice Management Endpoints
@app.get("/practice/info", response_model=PracticeResponse)
async def get_practice_info(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    practice = current_user.practice
    if not practice:
        raise HTTPException(status_code=404, detail="Practice not found")
    
    return PracticeResponse(
        id=practice.id,
        name=practice.name,
        subscription_plan=practice.subscription_plan.value,
        subscription_status=practice.subscription_status.value,
        max_providers=practice.max_providers,
        max_appointments_per_month=practice.max_appointments_per_month,
        appointments_this_month=practice.appointments_this_month or 0,
        total_revenue_saved=practice.total_revenue_saved or 0.0
    )

# Provider Management
@app.post("/providers")
async def create_provider(
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    specialty: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if practice has reached provider limit
    practice = current_user.practice
    current_providers = db.query(Provider).filter(Provider.practice_id == practice.id).count()
    
    if current_providers >= practice.max_providers:
        raise HTTPException(
            status_code=400,
            detail=f"Provider limit reached. Your plan allows {practice.max_providers} providers."
        )
    
    provider = Provider(
        practice_id=practice.id,
        name=name,
        email=email,
        phone=phone,
        specialty=specialty
    )
    
    db.add(provider)
    db.commit()
    db.refresh(provider)
    
    return {"message": "Provider created successfully", "provider_id": provider.id}

@app.get("/providers")
async def get_providers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    providers = db.query(Provider).filter(Provider.practice_id == current_user.practice_id).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "email": p.email,
            "phone": p.phone,
            "specialty": p.specialty,
            "total_appointments": p.total_appointments,
            "no_show_rate": p.no_show_rate
        }
        for p in providers
    ]

# Patient Management
@app.post("/patients")
async def create_patient(
    first_name: str,
    last_name: str,
    phone: str,
    email: Optional[str] = None,
    insurance_provider: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = Patient(
        practice_id=current_user.practice_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        insurance_provider=insurance_provider
    )
    
    db.add(patient)
    db.commit()
    db.refresh(patient)
    
    return {"message": "Patient created successfully", "patient_id": patient.id}

@app.get("/patients")
async def get_patients(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patients = db.query(Patient).filter(Patient.practice_id == current_user.practice_id).all()
    return [
        {
            "id": p.id,
            "name": p.get_full_name(),
            "email": p.email,
            "phone": p.phone,
            "total_appointments": p.total_appointments,
            "no_show_rate": p.no_show_rate,
            "risk_score": p.risk_score
        }
        for p in patients
    ]

# Appointment Management
@app.post("/appointments")
async def create_appointment(
    provider_id: str,
    patient_id: str,
    scheduled_time: datetime,
    duration_minutes: int = 30,
    appointment_type: str = "consultation",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    practice = current_user.practice
    
    # Check monthly appointment limit
    if practice.appointments_this_month >= practice.max_appointments_per_month:
        raise HTTPException(
            status_code=400,
            detail=f"Monthly appointment limit reached. Your plan allows {practice.max_appointments_per_month} appointments."
        )
    
    appointment = Appointment(
        practice_id=practice.id,
        provider_id=provider_id,
        patient_id=patient_id,
        scheduled_time=scheduled_time,
        duration_minutes=duration_minutes,
        appointment_type=appointment_type,
        status=AppointmentStatus.SCHEDULED
    )
    
    # Update practice appointment count
    practice.appointments_this_month = (practice.appointments_this_month or 0) + 1
    
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    
    return {"message": "Appointment created successfully", "appointment_id": appointment.id}

@app.get("/appointments")
async def get_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    appointments = db.query(Appointment).filter(
        Appointment.practice_id == current_user.practice_id
    ).offset(skip).limit(limit).all()
    
    return [
        {
            "id": a.id,
            "provider_id": a.provider_id,
            "patient_id": a.patient_id,
            "scheduled_time": a.scheduled_time,
            "duration_minutes": a.duration_minutes,
            "appointment_type": a.appointment_type,
            "status": a.status.value,
            "no_show_probability": a.no_show_probability
        }
        for a in appointments
    ]

# Dashboard Stats
@app.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    practice = current_user.practice
    
    # Get appointment counts
    total_appointments = db.query(Appointment).filter(
        Appointment.practice_id == practice.id
    ).count()
    
    # Get patient count
    active_patients = db.query(Patient).filter(
        Patient.practice_id == practice.id
    ).count()
    
    # Get high risk appointments (mock data for now)
    high_risk = db.query(Appointment).filter(
        Appointment.practice_id == practice.id,
        Appointment.no_show_probability > 0.3
    ).count()
    
    # Calculate trial days left
    trial_days_left = None
    if current_user.trial_end:
        trial_days_left = max(0, (current_user.trial_end - datetime.utcnow()).days)
    
    return {
        "total_appointments": total_appointments,
        "no_show_rate": 12.3,  # Mock data
        "revenue_saved": practice.total_revenue_saved or 0,
        "active_patients": active_patients,
        "upcoming_appointments": total_appointments,  # Simplified
        "high_risk_appointments": high_risk,
        "subscription_plan": practice.subscription_plan.value,
        "trial_days_left": trial_days_left
    }

# Subscription Plans (static data)
@app.get("/subscription/plans")
async def get_subscription_plans():
    return {
        "plans": {
            "trial": {
                "name": "Trial",
                "price": 0.0,
                "features": ["Basic scheduling", "Up to 100 appointments", "Email support"],
                "max_providers": 2,
                "max_appointments_per_month": 100
            },
            "starter": {
                "name": "Starter",
                "price": 49.0,
                "features": ["AI predictions", "Schedule optimization", "Up to 500 appointments", "Priority support"],
                "max_providers": 3,
                "max_appointments_per_month": 500
            },
            "professional": {
                "name": "Professional",
                "price": 99.0,
                "features": ["Advanced analytics", "Custom reports", "Up to 2000 appointments", "Phone support"],
                "max_providers": 10,
                "max_appointments_per_month": 2000
            },
            "enterprise": {
                "name": "Enterprise",
                "price": 199.0,
                "features": ["Multi-location", "API access", "Unlimited appointments", "Dedicated support"],
                "max_providers": 50,
                "max_appointments_per_month": 999999
            }
        }
    }

# Root endpoints
@app.get("/")
async def root():
    return {
        "service": "ChronoGuard Pro Database-Backed SaaS",
        "version": "3.0.0",
        "status": "operational",
        "features": ["Real Database", "Multi-tenant", "Subscription billing", "User authentication"]
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    # Test database connection
    try:
        user_count = db.query(User).count()
        return {
            "status": "healthy",
            "database": "connected",
            "users": user_count,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)