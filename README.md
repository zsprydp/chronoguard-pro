# ChronoGuard Pro

## AI-Powered Appointment Optimization Platform

ChronoGuard Pro is an intelligent B2B SaaS platform that helps healthcare practices and service businesses reduce revenue loss from no-shows through advanced AI predictions and automated schedule optimization.

**🔗 Repository:** https://github.com/zsprydp/chronoguard-pro

### Key Features
- 🤖 AI-powered no-show predictions with 85%+ accuracy
- 📊 Real-time schedule optimization and intelligent overbooking
- 💰 Revenue impact tracking and analytics
- 📱 Patient communication and automated reminders
- 🔄 Seamless calendar and EHR integrations
- 📈 Advanced analytics and industry benchmarking

### Tech Stack
- **Backend**: Python (FastAPI, SQLAlchemy, Celery)
- **ML/AI**: scikit-learn, TensorFlow, pandas
- **Database**: PostgreSQL, Redis
- **Frontend**: React with TypeScript, Tailwind CSS
- **Infrastructure**: Docker, Kubernetes, AWS/GCP

### Quick Start

#### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

#### Installation

1. Clone the repository:
```bash
git clone https://github.com/zsprydp/chronoguard-pro.git
cd chronoguard-pro
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the database:
```bash
createdb chronoguard_db
python -m alembic upgrade head
```

4. Start the services:

**Option 1 - Docker (Recommended):**
```bash
copy .env.example .env
docker-compose up -d
```

**Option 2 - Manual Setup:**
```bash
# Backend API (port 7000)
uvicorn app.main:app --reload --port 7000

# Celery worker (in another terminal)
celery -A app.celery worker --loglevel=info

# Frontend (in another terminal)
cd ../frontend
npm install
npm run dev
```

**Option 3 - Use Batch Script (Windows):**
```bash
# Run the startup script
start.bat
```

### Project Structure
```
chronoguard-pro/
├── backend/           # Python FastAPI backend
├── frontend/          # React TypeScript frontend
├── ml/               # Machine learning models and pipelines
├── docs/             # Documentation
└── tests/            # Test suites
```

### License
Proprietary - All Rights Reserved

### Access Points

After starting the application:

- **Frontend Dashboard**: http://localhost:7500
- **Backend API**: http://localhost:7000  
- **API Documentation**: http://localhost:7000/docs
- **Health Check**: http://localhost:7000/health

### Repository
- **GitHub**: https://github.com/zsprydp/chronoguard-pro
- **Local Path**: C:\Projects\chronoguard-pro

### Support
For support, create an issue on GitHub or email support@chronoguard.ai