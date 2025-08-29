#!/usr/bin/env python3
"""
ChronoGuard Pro Database Testing Script

This script provides comprehensive testing for the database-backed API.
It includes sample data creation and endpoint testing.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:7000"
TEST_USER_EMAIL = "test@chronoguard.com"
TEST_USER_PASSWORD = "testpassword123"

class ChronoGuardTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.access_token = None
        self.user_data = None
        self.practice_id = None
        self.provider_ids = []
        self.patient_ids = []
        self.appointment_ids = []

    def print_step(self, step: str):
        print(f"\n{'='*50}")
        print(f"Step: {step}")
        print(f"{'='*50}")

    def print_result(self, response: requests.Response, action: str):
        print(f"\n{action}:")
        print(f"Status: {response.status_code}")
        if response.status_code < 400:
            print("✅ SUCCESS")
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                return data
            except:
                print(f"Response: {response.text}")
                return None
        else:
            print("❌ FAILED")
            print(f"Error: {response.text}")
            return None

    def test_health_check(self):
        """Test the health check endpoint"""
        self.print_step("Testing Health Check")
        response = self.session.get(f"{self.base_url}/health")
        return self.print_result(response, "Health Check")

    def test_root_endpoint(self):
        """Test the root endpoint"""
        self.print_step("Testing Root Endpoint")
        response = self.session.get(f"{self.base_url}/")
        return self.print_result(response, "Root Endpoint")

    def test_subscription_plans(self):
        """Test subscription plans endpoint"""
        self.print_step("Testing Subscription Plans")
        response = self.session.get(f"{self.base_url}/subscription/plans")
        return self.print_result(response, "Subscription Plans")

    def test_user_registration(self):
        """Test user registration"""
        self.print_step("Testing User Registration")
        
        user_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "first_name": "Dr. John",
            "last_name": "Smith",
            "practice_name": "Smith Family Medicine",
            "phone": "555-0123"
        }
        
        response = self.session.post(f"{self.base_url}/auth/register", json=user_data)
        result = self.print_result(response, "User Registration")
        
        if result and 'access_token' in result:
            self.access_token = result['access_token']
            self.user_data = result['user']
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
            print(f"🔐 Access token obtained: {self.access_token[:20]}...")
        
        return result

    def test_user_login(self):
        """Test user login"""
        self.print_step("Testing User Login")
        
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
        result = self.print_result(response, "User Login")
        
        if result and 'access_token' in result:
            self.access_token = result['access_token']
            self.user_data = result['user']
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
            print(f"🔐 Logged in successfully")
        
        return result

    def test_practice_info(self):
        """Test getting practice information"""
        self.print_step("Testing Practice Info")
        response = self.session.get(f"{self.base_url}/practice/info")
        result = self.print_result(response, "Practice Info")
        
        if result:
            self.practice_id = result['id']
            print(f"📋 Practice ID: {self.practice_id}")
        
        return result

    def test_create_providers(self):
        """Test creating providers"""
        self.print_step("Testing Provider Creation")
        
        providers = [
            {
                "name": "Dr. Sarah Johnson",
                "email": "sarah.johnson@smithfamilymed.com",
                "phone": "555-0124",
                "specialty": "Family Medicine"
            },
            {
                "name": "Dr. Mike Wilson",
                "email": "mike.wilson@smithfamilymed.com", 
                "phone": "555-0125",
                "specialty": "Internal Medicine"
            }
        ]
        
        for provider in providers:
            response = self.session.post(f"{self.base_url}/providers", params=provider)
            result = self.print_result(response, f"Create Provider: {provider['name']}")
            if result and 'provider_id' in result:
                self.provider_ids.append(result['provider_id'])
        
        return self.provider_ids

    def test_get_providers(self):
        """Test getting all providers"""
        self.print_step("Testing Get Providers")
        response = self.session.get(f"{self.base_url}/providers")
        return self.print_result(response, "Get Providers")

    def test_create_patients(self):
        """Test creating patients"""
        self.print_step("Testing Patient Creation")
        
        patients = [
            {
                "first_name": "Alice",
                "last_name": "Brown",
                "phone": "555-1001",
                "email": "alice.brown@email.com",
                "insurance_provider": "Blue Cross"
            },
            {
                "first_name": "Bob",
                "last_name": "Davis",
                "phone": "555-1002", 
                "email": "bob.davis@email.com",
                "insurance_provider": "Aetna"
            },
            {
                "first_name": "Carol",
                "last_name": "Miller",
                "phone": "555-1003",
                "email": "carol.miller@email.com",
                "insurance_provider": "Humana"
            }
        ]
        
        for patient in patients:
            response = self.session.post(f"{self.base_url}/patients", params=patient)
            result = self.print_result(response, f"Create Patient: {patient['first_name']} {patient['last_name']}")
            if result and 'patient_id' in result:
                self.patient_ids.append(result['patient_id'])
        
        return self.patient_ids

    def test_get_patients(self):
        """Test getting all patients"""
        self.print_step("Testing Get Patients")
        response = self.session.get(f"{self.base_url}/patients")
        return self.print_result(response, "Get Patients")

    def test_create_appointments(self):
        """Test creating appointments"""
        self.print_step("Testing Appointment Creation")
        
        if not self.provider_ids or not self.patient_ids:
            print("❌ No providers or patients available for appointment creation")
            return []
        
        # Create appointments for the next few days
        appointments = []
        base_time = datetime.now() + timedelta(days=1)
        
        for i in range(min(3, len(self.patient_ids))):
            appointment_time = base_time + timedelta(hours=i*2)
            appointment_data = {
                "provider_id": self.provider_ids[i % len(self.provider_ids)],
                "patient_id": self.patient_ids[i],
                "scheduled_time": appointment_time.isoformat(),
                "duration_minutes": 30,
                "appointment_type": "consultation"
            }
            
            response = self.session.post(f"{self.base_url}/appointments", json=appointment_data)
            result = self.print_result(response, f"Create Appointment {i+1}")
            if result and 'appointment_id' in result:
                self.appointment_ids.append(result['appointment_id'])
        
        return self.appointment_ids

    def test_get_appointments(self):
        """Test getting all appointments"""
        self.print_step("Testing Get Appointments")
        response = self.session.get(f"{self.base_url}/appointments")
        return self.print_result(response, "Get Appointments")

    def test_dashboard_stats(self):
        """Test getting dashboard statistics"""
        self.print_step("Testing Dashboard Stats")
        response = self.session.get(f"{self.base_url}/dashboard/stats")
        return self.print_result(response, "Dashboard Stats")

    def run_full_test_suite(self):
        """Run the complete test suite"""
        print("🚀 Starting ChronoGuard Pro Database Test Suite")
        print(f"Testing against: {self.base_url}")
        
        try:
            # Basic endpoint tests
            self.test_health_check()
            self.test_root_endpoint()
            self.test_subscription_plans()
            
            # Authentication tests
            self.test_user_registration()
            
            # Skip login test if registration worked (already logged in)
            if not self.access_token:
                self.test_user_login()
            
            if not self.access_token:
                print("❌ Authentication failed - cannot continue with protected endpoints")
                return
            
            # Protected endpoint tests
            self.test_practice_info()
            self.test_create_providers()
            self.test_get_providers()
            self.test_create_patients()
            self.test_get_patients()
            self.test_create_appointments()
            self.test_get_appointments()
            self.test_dashboard_stats()
            
            # Summary
            print(f"\n{'='*60}")
            print("🎉 TEST SUITE COMPLETED!")
            print(f"{'='*60}")
            print(f"Providers created: {len(self.provider_ids)}")
            print(f"Patients created: {len(self.patient_ids)}")
            print(f"Appointments created: {len(self.appointment_ids)}")
            print(f"Practice ID: {self.practice_id}")
            print(f"Access Token: {'✅ Obtained' if self.access_token else '❌ Failed'}")
            
        except KeyboardInterrupt:
            print("\n❌ Test interrupted by user")
        except Exception as e:
            print(f"\n❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    tester = ChronoGuardTester()
    tester.run_full_test_suite()