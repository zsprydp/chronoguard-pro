#!/usr/bin/env python3
"""
ChronoGuard Pro Database Initialization Script

This script initializes the database, runs migrations, and optionally creates sample data.
"""

import os
import sys
import subprocess
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent))

from app.database import Base, get_db, engine
from app.models import User, Practice, Provider, Patient, Appointment, SubscriptionPlan, SubscriptionStatus

# Load environment variables
load_dotenv()

def check_database_exists():
    """Check if database exists and is accessible"""
    print("Checking database connection...")
    try:
        # Try to connect to the database
        connection = engine.connect()
        connection.close()
        print("SUCCESS: Database connection successful")
        return True
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        return False

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("SUCCESS: Database tables created successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create tables: {e}")
        return False

def run_alembic_migrations():
    """Run Alembic migrations if available"""
    print("Running database migrations...")
    try:
        # Check if alembic is available
        result = subprocess.run(['alembic', '--help'], capture_output=True, text=True)
        if result.returncode != 0:
            print("WARNING: Alembic not found, skipping migrations")
            return True
        
        # Initialize alembic if not already initialized
        if not Path('alembic').exists():
            print("Initializing Alembic...")
            subprocess.run(['alembic', 'init', 'alembic'], check=True)
        
        # Generate initial migration if no migrations exist
        versions_dir = Path('alembic/versions')
        if not versions_dir.exists() or not list(versions_dir.glob('*.py')):
            print("Creating initial migration...")
            subprocess.run(['alembic', 'revision', '--autogenerate', '-m', 'Initial migration'], check=True)
        
        # Run migrations
        print("Running migrations...")
        subprocess.run(['alembic', 'upgrade', 'head'], check=True)
        print("SUCCESS: Migrations completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Migration failed: {e}")
        return False
    except Exception as e:
        print(f"WARNING: Migration skipped: {e}")
        return True

def check_existing_data():
    """Check if database already has data"""
    print("Checking for existing data...")
    try:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        user_count = db.query(User).count()
        practice_count = db.query(Practice).count()
        
        db.close()
        
        if user_count > 0 or practice_count > 0:
            print(f"INFO: Found existing data: {user_count} users, {practice_count} practices")
            return True
        else:
            print("INFO: Database is empty")
            return False
    except Exception as e:
        print(f"ERROR: Failed to check existing data: {e}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    print("Creating sample data...")
    try:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Create sample practice
        sample_practice = Practice(
            name="Demo Medical Practice",
            subscription_plan=SubscriptionPlan.TRIAL,
            subscription_status=SubscriptionStatus.TRIAL,
            max_providers=2,
            max_appointments_per_month=100
        )
        db.add(sample_practice)
        db.flush()
        
        # Create sample user
        sample_user = User(
            email="demo@chronoguard.com",
            first_name="Demo",
            last_name="User",
            phone="555-DEMO",
            role="practice_owner",
            practice_id=sample_practice.id,
            is_verified=True
        )
        sample_user.set_password("demo123")
        db.add(sample_user)
        
        # Create sample providers
        providers = [
            Provider(
                practice_id=sample_practice.id,
                name="Dr. Emily Johnson",
                email="emily.johnson@demo.com",
                specialty="Family Medicine"
            ),
            Provider(
                practice_id=sample_practice.id,
                name="Dr. Michael Chen",
                email="michael.chen@demo.com", 
                specialty="Internal Medicine"
            )
        ]
        db.add_all(providers)
        db.flush()
        
        # Create sample patients
        patients = [
            Patient(
                practice_id=sample_practice.id,
                first_name="John",
                last_name="Doe",
                email="john.doe@email.com",
                phone="555-0001",
                insurance_provider="Blue Cross"
            ),
            Patient(
                practice_id=sample_practice.id,
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@email.com",
                phone="555-0002",
                insurance_provider="Aetna"
            )
        ]
        db.add_all(patients)
        
        db.commit()
        db.close()
        
        print("SUCCESS: Sample data created successfully")
        print("INFO: Demo login: demo@chronoguard.com / demo123")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create sample data: {e}")
        return False

def main():
    """Main initialization function"""
    print("ChronoGuard Pro Database Initialization")
    print("=" * 50)
    
    # Check database connection
    if not check_database_exists():
        return False
    
    # Create tables
    if not create_tables():
        return False
    
    # Run migrations
    if not run_alembic_migrations():
        print("⚠️  Continuing without migrations...")
    
    # Check for existing data
    has_data = check_existing_data()
    
    # Create sample data if database is empty
    if not has_data:
        print("\nCreating sample data automatically...")
        create_sample_data()
    
    print("\n" + "=" * 50)
    print("Database initialization completed!")
    print("\nNext steps:")
    print("1. Start the backend server: python -m uvicorn db_main:app --reload --port 7000")
    print("2. Test the API using: python test_database.py")
    print("3. Visit the docs at: http://localhost:7000/docs")
    
    if has_data:
        print("\nNote: Database already contains data")
    else:
        print("\nDemo account: demo@chronoguard.com / demo123")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)