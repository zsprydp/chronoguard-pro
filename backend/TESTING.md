# ChronoGuard Pro Database Testing Guide

This guide provides multiple ways to test the database-backed API endpoints.

## Quick Start

1. **Initialize Database:**
   ```bash
   cd backend
   python init_database.py
   ```

2. **Start API Server:**
   ```bash
   python -m uvicorn db_main:app --reload --port 7000
   ```

3. **Run Automated Tests:**
   ```bash
   python test_database.py
   ```

## Testing Methods

### Method 1: Automated Python Test Script
The easiest way to test all endpoints:

```bash
cd backend
python test_database.py
```

This will:
- Test all API endpoints
- Create sample data
- Verify database operations
- Show detailed results

### Method 2: Interactive API Documentation
Visit the auto-generated API docs:
- Open browser to: http://localhost:7000/docs
- Interactive Swagger UI with all endpoints
- Try endpoints directly in browser
- See request/response schemas

### Method 3: Manual cURL Testing

#### Basic Endpoints (No Authentication Required)

**Health Check:**
```bash
curl http://localhost:7000/health
```

**Root Info:**
```bash
curl http://localhost:7000/
```

**Subscription Plans:**
```bash
curl http://localhost:7000/subscription/plans
```

#### Authentication Endpoints

**Register New User:**
```bash
curl -X POST http://localhost:7000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "first_name": "John",
    "last_name": "Doe",
    "practice_name": "Test Practice",
    "phone": "555-0123"
  }'
```

**Login User:**
```bash
curl -X POST http://localhost:7000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com", 
    "password": "testpass123"
  }'
```

Save the `access_token` from the response for authenticated requests.

#### Authenticated Endpoints
Replace `YOUR_TOKEN` with the actual token from login/register:

**Get Practice Info:**
```bash
curl http://localhost:7000/practice/info \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Create Provider:**
```bash
curl -X POST "http://localhost:7000/providers?name=Dr.%20Smith&email=smith@practice.com&specialty=Cardiology" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Get All Providers:**
```bash
curl http://localhost:7000/providers \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Create Patient:**
```bash
curl -X POST "http://localhost:7000/patients?first_name=Alice&last_name=Johnson&phone=555-0001&email=alice@email.com" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Get All Patients:**
```bash
curl http://localhost:7000/patients \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Create Appointment:**
```bash
curl -X POST http://localhost:7000/appointments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "provider_id": "PROVIDER_ID",
    "patient_id": "PATIENT_ID", 
    "scheduled_time": "2024-12-01T10:00:00",
    "duration_minutes": 30,
    "appointment_type": "consultation"
  }'
```

**Get Dashboard Stats:**
```bash
curl http://localhost:7000/dashboard/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Method 4: Database Direct Testing

**Check Database File:**
```bash
# For SQLite
ls -la chronoguard.db

# View tables using sqlite3
sqlite3 chronoguard.db ".tables"

# Check user count
sqlite3 chronoguard.db "SELECT COUNT(*) FROM users;"
```

**View Database Contents:**
```bash
# Show all practices
sqlite3 chronoguard.db "SELECT * FROM practices;"

# Show all users
sqlite3 chronoguard.db "SELECT id, email, first_name, last_name, role FROM users;"

# Show appointments with joins
sqlite3 chronoguard.db "
  SELECT a.id, p.name as provider, pt.first_name || ' ' || pt.last_name as patient, 
         a.scheduled_time, a.status 
  FROM appointments a 
  JOIN providers p ON a.provider_id = p.id 
  JOIN patients pt ON a.patient_id = pt.id;
"
```

## Test Data Structure

When running tests, the following data structure is created:

### Practice
- Name: "Smith Family Medicine" or "Demo Medical Practice"
- Subscription: Trial (14 days)
- Limits: 2 providers, 100 appointments/month

### Users
- Practice Owner: test@chronoguard.com or demo@chronoguard.com
- Role: practice_owner
- Password: testpassword123 or demo123

### Providers
- Dr. Sarah Johnson (Family Medicine)
- Dr. Mike Wilson (Internal Medicine)

### Patients
- Alice Brown (Blue Cross)
- Bob Davis (Aetna)
- Carol Miller (Humana)

### Appointments
- Multiple appointments scheduled for next few days
- Various providers and patients
- 30-minute consultations

## Expected Results

### Successful Registration Response
```json
{
  "message": "Registration successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-string",
    "email": "test@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "practice_owner",
    "subscription_status": "trial",
    "trial_days_left": 14,
    "is_verified": false,
    "practice_name": "Test Practice"
  }
}
```

### Successful Dashboard Stats Response
```json
{
  "total_appointments": 3,
  "no_show_rate": 12.3,
  "revenue_saved": 0,
  "active_patients": 3,
  "upcoming_appointments": 3,
  "high_risk_appointments": 0,
  "subscription_plan": "trial",
  "trial_days_left": 14
}
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```
   Solution: Run python init_database.py first
   ```

2. **Authentication Failed (401)**
   ```
   Solution: Check token in Authorization header
   Format: "Bearer YOUR_TOKEN_HERE"
   ```

3. **Provider/Patient Not Found**
   ```
   Solution: Create providers and patients first before appointments
   Use the correct IDs from creation responses
   ```

4. **Monthly Limit Reached**
   ```
   Solution: Trial accounts limited to 100 appointments/month
   Check dashboard stats for current usage
   ```

### Debugging Commands

**Check Server Status:**
```bash
curl http://localhost:7000/health
```

**Verify Database Tables:**
```bash
python -c "
from app.database import engine
from app.models import Base
print('Tables:', Base.metadata.tables.keys())
"
```

**Reset Database:**
```bash
rm chronoguard.db  # Remove SQLite file
python init_database.py  # Recreate
```

## Performance Testing

### Load Testing with Multiple Users
```bash
# Create 10 users quickly
for i in {1..10}; do
  curl -X POST http://localhost:7000/auth/register \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"user$i@test.com\",\"password\":\"pass123\",\"first_name\":\"User\",\"last_name\":\"$i\",\"practice_name\":\"Practice $i\"}" &
done
wait
```

### Concurrent Requests
```bash
# Multiple simultaneous health checks
for i in {1..5}; do
  curl http://localhost:7000/health &
done
wait
```

## Integration with Frontend

1. **Start both servers:**
   ```bash
   # Terminal 1 - Backend
   cd backend && python -m uvicorn db_main:app --reload --port 7000
   
   # Terminal 2 - Frontend  
   cd frontend && npm run dev -- --port 7500
   ```

2. **Test full stack:**
   - Frontend: http://localhost:7500
   - Backend API: http://localhost:7000
   - API Docs: http://localhost:7000/docs

The frontend should now connect to the real database instead of mock data.

## Security Testing

### Token Validation
```bash
# Test with invalid token
curl http://localhost:7000/practice/info \
  -H "Authorization: Bearer invalid_token"
```

### SQL Injection Protection
```bash
# Test malicious input (should be handled safely)
curl -X POST http://localhost:7000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"'; DROP TABLE users; --"}'
```

The system should handle these safely with parameterized queries.