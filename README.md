# ChronoGuard Pro

## AI-Powered Appointment Optimization SaaS Platform

ChronoGuard Pro is an intelligent B2B SaaS platform that helps healthcare practices and service businesses reduce revenue loss from no-shows through advanced AI predictions and automated schedule optimization.

**🔗 Repository:** https://github.com/zsprydp/chronoguard-pro

### ✨ Key Features
- 🤖 AI-powered no-show predictions with risk assessment
- 📊 Real-time schedule optimization and intelligent recommendations  
- 💰 Revenue impact tracking and analytics dashboard
- 📱 Modern responsive UI with intuitive design
- 🔐 Multi-tenant SaaS architecture with subscription management
- 🗄️ Complete database integration with real data persistence
- 📈 Interactive appointment management with color-coded risk levels

### 🛠️ Tech Stack
- **Backend**: Python (FastAPI, SQLAlchemy, Alembic)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **UI Components**: Custom design system with accessibility features
- **Authentication**: JWT tokens with secure password hashing
- **Development**: Hot reload, automated testing, comprehensive documentation

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (for backend API)
- **Node.js 18+** (for frontend)
- **Git** (for cloning repository)

*No database setup required - uses SQLite out of the box!*

### ⚡ One-Click Startup (Windows)

1. **Clone the repository:**
```bash
git clone https://github.com/zsprydp/chronoguard-pro.git
cd chronoguard-pro
```

2. **Run the startup script:**
```bash
start.bat
```

That's it! The script will:
- ✅ Check prerequisites  
- ✅ Install dependencies
- ✅ Initialize the SQLite database
- ✅ Start both backend and frontend servers
- ✅ Open in separate windows so you can close the main terminal

### 🔧 Manual Setup (Alternative)

**Backend Setup:**
```bash
cd backend
pip install -r requirements.txt
python init_database.py
python -m uvicorn app.db_main:app --reload --port 7000
```

**Frontend Setup (in another terminal):**
```bash
cd frontend
npm install
npm run dev -- --port 7501
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

## 📍 Access Points

After starting the application:

- **🌐 Frontend Dashboard**: http://localhost:7501
- **🔗 Backend API**: http://localhost:7000  
- **📚 API Documentation**: http://localhost:7000/docs
- **❤️ Health Check**: http://localhost:7000/health

### 🔑 Demo Login Credentials
- **Email**: `demo@chronoguard.com`
- **Password**: `demo123`

*Or create a new account via the registration page*

## 🛑 Stopping the Application

### Using the Stop Script:
```bash
stop.bat
```

### Manual Stop:
- Close the backend and frontend command windows
- Or use Ctrl+C in each terminal

The applications will continue running independently in their own windows until explicitly stopped, allowing you to close the main terminal while keeping the servers running.

## 📂 Project Structure
```
chronoguard-pro/
├── backend/              # Python FastAPI backend
│   ├── app/             # Application code
│   ├── alembic/         # Database migrations  
│   ├── chronoguard.db   # SQLite database
│   └── *.py             # Database scripts & tests
├── frontend/            # Next.js React frontend
│   └── src/             # Frontend source code
├── start.bat           # Windows startup script
├── stop.bat            # Windows stop script  
└── README.md           # This file
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
cd backend
python test_database.py
```

Or test specific endpoints:
```bash
python simple_test.py
```

See `backend/TESTING.md` for detailed testing instructions.

### Repository
- **GitHub**: https://github.com/zsprydp/chronoguard-pro
- **Local Path**: C:\Projects\chronoguard-pro

### Support
For support, create an issue on GitHub or email support@chronoguard.ai