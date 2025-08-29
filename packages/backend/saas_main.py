from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional, List
import jwt
import os
from passlib.context import CryptContext

# Initialize FastAPI app
app = FastAPI(
    title="ChronoGuard Pro - SaaS API",
    description="AI-Powered Appointment Optimization SaaS Platform",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7500", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "chronoguard-secret-key-change-in-production")
ALGORITHM = "HS256"

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

class SubscriptionPlan(BaseModel):
    name: str
    price: float
    features: List[str]
    max_providers: int
    max_appointments_per_month: int

# Mock user storage (replace with database in production)
users_db = {}
practices_db = {}

# Subscription Plans
SUBSCRIPTION_PLANS = {
    "trial": SubscriptionPlan(
        name="Trial",
        price=0.0,
        features=["Basic scheduling", "Up to 100 appointments", "Email support"],
        max_providers=2,
        max_appointments_per_month=100
    ),
    "starter": SubscriptionPlan(
        name="Starter",
        price=49.0,
        features=["AI predictions", "Schedule optimization", "Up to 500 appointments", "Priority support"],
        max_providers=3,
        max_appointments_per_month=500
    ),
    "professional": SubscriptionPlan(
        name="Professional", 
        price=99.0,
        features=["Advanced analytics", "Custom reports", "Up to 2000 appointments", "Phone support"],
        max_providers=10,
        max_appointments_per_month=2000
    ),
    "enterprise": SubscriptionPlan(
        name="Enterprise",
        price=199.0,
        features=["Multi-location", "API access", "Unlimited appointments", "Dedicated support"],
        max_providers=50,
        max_appointments_per_month=999999
    )
}

# Helper functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
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

def get_current_user(user_id: str = Depends(verify_token)):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Authentication Endpoints
@app.post("/auth/register", response_model=dict)
async def register(user_data: UserRegister):
    # Check if user exists
    if any(u["email"] == user_data.email for u in users_db.values()):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_id = f"user_{len(users_db) + 1}"
    practice_id = f"practice_{len(practices_db) + 1}"
    
    # Hash password
    hashed_password = pwd_context.hash(user_data.password)
    
    # Create practice
    practices_db[practice_id] = {
        "id": practice_id,
        "name": user_data.practice_name,
        "owner_id": user_id,
        "subscription_plan": "trial",
        "created_at": datetime.utcnow()
    }
    
    # Create user
    users_db[user_id] = {
        "id": user_id,
        "email": user_data.email,
        "password_hash": hashed_password,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "phone": user_data.phone,
        "role": "practice_owner",
        "practice_id": practice_id,
        "subscription_status": "trial",
        "trial_start": datetime.utcnow(),
        "trial_end": datetime.utcnow() + timedelta(days=14),
        "is_verified": False,
        "created_at": datetime.utcnow()
    }
    
    # Create access token
    access_token = create_access_token(data={"sub": user_id})
    
    return {
        "message": "Registration successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user_id,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role="practice_owner",
            subscription_status="trial",
            trial_days_left=14,
            is_verified=False
        )
    }

@app.post("/auth/login")
async def login(login_data: UserLogin):
    # Find user
    user = None
    for u in users_db.values():
        if u["email"] == login_data.email:
            user = u
            break
    
    if not user or not pwd_context.verify(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Update last login
    user["last_login"] = datetime.utcnow()
    user["login_count"] = user.get("login_count", 0) + 1
    
    # Calculate trial days left
    trial_days_left = None
    if user["subscription_status"] == "trial" and user.get("trial_end"):
        trial_days_left = max(0, (user["trial_end"] - datetime.utcnow()).days)
    
    # Create access token
    access_token = create_access_token(data={"sub": user["id"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user["id"],
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            role=user["role"],
            subscription_status=user["subscription_status"],
            trial_days_left=trial_days_left,
            is_verified=user["is_verified"]
        )
    }

# Subscription Endpoints
@app.get("/subscription/plans")
async def get_subscription_plans():
    return {"plans": SUBSCRIPTION_PLANS}

@app.get("/subscription/current")
async def get_current_subscription(current_user = Depends(get_current_user)):
    practice = practices_db.get(current_user["practice_id"])
    plan = SUBSCRIPTION_PLANS.get(practice["subscription_plan"], SUBSCRIPTION_PLANS["trial"])
    
    return {
        "current_plan": practice["subscription_plan"],
        "plan_details": plan,
        "subscription_status": current_user["subscription_status"],
        "trial_days_left": max(0, (current_user["trial_end"] - datetime.utcnow()).days) if current_user.get("trial_end") else None
    }

@app.post("/subscription/upgrade")
async def upgrade_subscription(plan_name: str, current_user = Depends(get_current_user)):
    if plan_name not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    # In a real app, integrate with Stripe here
    practice = practices_db[current_user["practice_id"]]
    practice["subscription_plan"] = plan_name
    current_user["subscription_status"] = "active"
    
    return {
        "message": f"Successfully upgraded to {plan_name}",
        "new_plan": SUBSCRIPTION_PLANS[plan_name]
    }

# Dashboard Endpoints
@app.get("/dashboard/stats")
async def get_dashboard_stats(current_user = Depends(get_current_user)):
    # Mock data - replace with real calculations
    return {
        "total_appointments": 145,
        "no_show_rate": 12.3,
        "revenue_saved": 8750,
        "active_patients": 89,
        "upcoming_appointments": 23,
        "high_risk_appointments": 5,
        "subscription_plan": practices_db[current_user["practice_id"]]["subscription_plan"],
        "trial_days_left": max(0, (current_user["trial_end"] - datetime.utcnow()).days) if current_user.get("trial_end") else None
    }

# Practice Management
@app.get("/practice/info")
async def get_practice_info(current_user = Depends(get_current_user)):
    practice = practices_db[current_user["practice_id"]]
    return practice

@app.put("/practice/info")
async def update_practice_info(practice_name: str, current_user = Depends(get_current_user)):
    practice = practices_db[current_user["practice_id"]]
    practice["name"] = practice_name
    practice["updated_at"] = datetime.utcnow()
    return {"message": "Practice updated successfully"}

# Feature Access Control
@app.get("/features/check/{feature_name}")
async def check_feature_access(feature_name: str, current_user = Depends(get_current_user)):
    practice = practices_db[current_user["practice_id"]]
    plan = SUBSCRIPTION_PLANS[practice["subscription_plan"]]
    
    # Feature access logic
    has_access = True
    if current_user["subscription_status"] == "trial":
        trial_expired = current_user["trial_end"] < datetime.utcnow()
        has_access = not trial_expired
    elif current_user["subscription_status"] != "active":
        has_access = False
    
    return {
        "feature": feature_name,
        "has_access": has_access,
        "plan": practice["subscription_plan"],
        "reason": "Trial expired" if not has_access and current_user["subscription_status"] == "trial" else None
    }

# Root endpoints
@app.get("/")
async def root():
    return {
        "service": "ChronoGuard Pro SaaS",
        "version": "2.0.0",
        "status": "operational",
        "features": ["Multi-tenant", "Subscription billing", "User authentication"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# User Profile
@app.get("/profile", response_model=UserResponse)
async def get_profile(current_user = Depends(get_current_user)):
    trial_days_left = None
    if current_user["subscription_status"] == "trial" and current_user.get("trial_end"):
        trial_days_left = max(0, (current_user["trial_end"] - datetime.utcnow()).days)
    
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        role=current_user["role"],
        subscription_status=current_user["subscription_status"],
        trial_days_left=trial_days_left,
        is_verified=current_user["is_verified"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)