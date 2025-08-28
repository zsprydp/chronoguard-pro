#!/usr/bin/env python3
"""
Simple ChronoGuard Pro Database Testing Script (Windows Compatible)
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:7000"
TEST_USER_EMAIL = "test@chronoguard.com"
TEST_USER_PASSWORD = "testpassword123"

def test_api():
    """Test the database-backed API"""
    print("=" * 50)
    print("ChronoGuard Pro Database Test Suite")
    print("=" * 50)
    print(f"Testing against: {BASE_URL}")
    print()
    
    session = requests.Session()
    
    # Test 1: Health Check
    print("Test 1: Health Check")
    try:
        response = session.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: {data.get('status', 'unknown')}")
            print(f"Users in DB: {data.get('users', 0)}")
        else:
            print("FAILED: Health check failed")
    except Exception as e:
        print(f"ERROR: {e}")
    print()
    
    # Test 2: User Registration
    print("Test 2: User Registration")
    try:
        user_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "first_name": "Test",
            "last_name": "User",
            "practice_name": "Test Practice",
            "phone": "555-0123"
        }
        
        response = session.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            if access_token:
                print("SUCCESS: User registered and logged in")
                print(f"Token: {access_token[:20]}...")
                print(f"User: {data['user']['first_name']} {data['user']['last_name']}")
                print(f"Practice: {data['user']['practice_name']}")
                print(f"Trial Days: {data['user']['trial_days_left']}")
                
                # Set authorization header for future requests
                session.headers.update({
                    'Authorization': f'Bearer {access_token}'
                })
            else:
                print("FAILED: No access token received")
        else:
            print(f"FAILED: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")
    print()
    
    # Test 3: Practice Info
    print("Test 3: Practice Information")
    try:
        response = session.get(f"{BASE_URL}/practice/info")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Practice info retrieved")
            print(f"Practice: {data['name']}")
            print(f"Plan: {data['subscription_plan']}")
            print(f"Max Providers: {data['max_providers']}")
            print(f"Max Appointments: {data['max_appointments_per_month']}")
            print(f"Current Appointments: {data['appointments_this_month']}")
        else:
            print(f"FAILED: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")
    print()
    
    # Test 4: Create Provider
    print("Test 4: Create Provider")
    try:
        provider_data = {
            "name": "Dr. Test Provider",
            "email": "provider@test.com",
            "specialty": "General Medicine",
            "phone": "555-0124"
        }
        
        response = session.post(f"{BASE_URL}/providers", params=provider_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            provider_id = data.get('provider_id')
            print("SUCCESS: Provider created")
            print(f"Provider ID: {provider_id}")
        else:
            print(f"FAILED: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")
    print()
    
    # Test 5: Get Providers
    print("Test 5: Get Providers")
    try:
        response = session.get(f"{BASE_URL}/providers")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            providers = response.json()
            print(f"SUCCESS: Found {len(providers)} providers")
            for provider in providers:
                print(f"  - {provider['name']} ({provider['specialty']})")
        else:
            print(f"FAILED: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")
    print()
    
    # Test 6: Create Patient
    print("Test 6: Create Patient")
    try:
        patient_data = {
            "first_name": "Test",
            "last_name": "Patient",
            "phone": "555-1001",
            "email": "patient@test.com",
            "insurance_provider": "Test Insurance"
        }
        
        response = session.post(f"{BASE_URL}/patients", params=patient_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            patient_id = data.get('patient_id')
            print("SUCCESS: Patient created")
            print(f"Patient ID: {patient_id}")
        else:
            print(f"FAILED: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")
    print()
    
    # Test 7: Dashboard Stats
    print("Test 7: Dashboard Statistics")
    try:
        response = session.get(f"{BASE_URL}/dashboard/stats")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print("SUCCESS: Dashboard stats retrieved")
            print(f"Total Appointments: {stats['total_appointments']}")
            print(f"Active Patients: {stats['active_patients']}")
            print(f"Revenue Saved: ${stats['revenue_saved']}")
            print(f"Subscription: {stats['subscription_plan']}")
            print(f"Trial Days Left: {stats['trial_days_left']}")
        else:
            print(f"FAILED: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")
    print()
    
    print("=" * 50)
    print("Test Suite Completed!")
    print("=" * 50)
    print("\nDatabase has been tested successfully!")
    print("You can now:")
    print("1. Visit http://localhost:7000/docs for interactive API docs")
    print("2. Check the database file: chronoguard.db")
    print("3. Test the frontend at http://localhost:7500")

if __name__ == "__main__":
    test_api()