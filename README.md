# ChronoGuard Pro - Monorepo

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

## 🏗️ Monorepo Structure

```
chronoguard-pro/
├── packages/
│   ├── backend/          # Python FastAPI backend
│   ├── frontend/         # Next.js React frontend
│   ├── ml/              # Machine learning models and pipelines
│   └── shared/          # Shared utilities and types
├── scripts/             # Development and deployment scripts
├── docker-compose.yml   # Multi-service Docker setup
├── package.json         # Root package.json with workspace config
└── README.md           # This file
```

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
scripts\dev.bat
```

That's it! The script will:
- ✅ Check prerequisites  
- ✅ Install dependencies
- ✅ Initialize the SQLite database
- ✅ Start both backend and frontend servers
- ✅ Open in separate windows so you can close the main terminal

### 🔧 Manual Setup (Alternative)

**Install all dependencies:**
```bash
npm run install:all
```

**Start development servers:**
```bash
npm run dev
```

**Or start individually:**
```bash
# Backend (Terminal 1)
npm run dev:backend

# Frontend (Terminal 2)  
npm run dev:frontend
```

### 🐳 Docker Setup

**Start all services with Docker:**
```bash
npm run docker:up
```

**Stop all services:**
```bash
npm run docker:down
```

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
scripts\stop.bat
```

### Manual Stop:
- Close the backend and frontend command windows
- Or use Ctrl+C in each terminal

## 📦 Package Management

This monorepo uses npm workspaces for package management:

```bash
# Install dependencies for all packages
npm install

# Install dependencies for a specific package
cd packages/frontend && npm install

# Run scripts across all packages
npm run dev          # Start all services
npm run build        # Build all packages
npm run test         # Test all packages
npm run lint         # Lint all packages
```

## 🧪 Testing

```bash
# Test all packages
npm run test

# Test specific package
npm run test:frontend
npm run test:backend
```

## 🚀 Deployment

```bash
# Build for production
npm run build

# Start production servers
npm run start

# Deploy with Docker
npm run docker:build
npm run docker:up
```

## 🔧 Development

### Adding New Packages

1. Create new directory in `packages/`
2. Add `package.json` with appropriate name (`@chronoguard/package-name`)
3. Update root `package.json` scripts if needed

### Database Management

```bash
# Initialize database
npm run db:init

# Run migrations
npm run db:migrate

# Reset database
npm run db:reset
```

## 📝 License
Proprietary - All Rights Reserved

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support and questions, please contact the development team.